import fs from 'node:fs';
import path from 'node:path';

interface HastNode {
  /** Child nodes of this element. */
  children?: HastNode[];
  /** HTML attributes assigned to the element. */
  properties?: Record<string, unknown>;
  /** The HTML tag name (e.g., `a`, `span`). */
  tagName?: string;
  /** The type of node (e.g., `text`, `element`). */
  type?: string;
  /** The string content if the node is a text node. */
  value?: string;
}

interface SpanInfo {
  /** End character offset of the span in the reconstructed line. */
  end: number;
  /** The AST span node. */
  node: HastNode;
  /** Start character offset of the span in the reconstructed line. */
  start: number;
  /** Text content of the span. */
  text: string;
}

function isInsideStringOrComment(lineText: string, targetIndex: number): boolean {
  let quoteChar: string | undefined = undefined;
  let isTriple = false;
  let isEscaped = false;
  let idx = 0;

  while (idx < targetIndex) {
    const char = lineText[idx];

    if (isEscaped) {
      isEscaped = false;
      idx += 1;
    } else if (char === '\\') {
      isEscaped = true;
      idx += 1;
    } else if (quoteChar === undefined) {
      if (char === '#') {
        return true;
      }

      const nextThree = lineText.substring(idx, idx + 3);
      if (nextThree === "'''" || nextThree === '"""') {
        quoteChar = char;
        isTriple = true;
        idx += 3;
      } else if (char === "'" || char === '"') {
        quoteChar = char;
        isTriple = false;
        idx += 1;
      } else {
        idx += 1;
      }
    } else if (isTriple) {
      const nextThree = lineText.substring(idx, idx + 3);
      if (nextThree === quoteChar.repeat(3)) {
        quoteChar = undefined;
        isTriple = false;
        idx += 3;
      } else {
        idx += 1;
      }
    } else if (char === quoteChar) {
      quoteChar = undefined;
      idx += 1;
    } else {
      idx += 1;
    }
  }

  return quoteChar !== undefined;
}

function shouldLinkMatch(
  lineText: string,
  match: RegExpMatchArray,
  defName: string | undefined
): boolean {
  const [matchedStr] = match;
  const matchIndex = match.index ?? 0;

  // [1] Skip if matching the defined name of this code block:
  if (defName && matchedStr === defName) {
    return false;
  }

  // [2] Skip if inside string literal or comment:
  if (isInsideStringOrComment(lineText, matchIndex)) {
    return false;
  }

  const textBefore = lineText.substring(0, matchIndex);
  const textAfter = lineText.substring(matchIndex + matchedStr.length);
  const trimmedBefore = textBefore.trimEnd();
  const trimmedAfter = textAfter.trimStart();

  // [3] Skip if definition name (`def ...` or `class ...`):
  if (/\b(?:def|class|async\s+def)\s+$/.test(textBefore)) {
    return false;
  }

  // [4] Skip if alias after `as` or instance attribute on `self.` / `cls.`:
  if (/\bas\s+$/.test(textBefore) || /\b(?:self|cls)\.\s*$/.test(textBefore)) {
    return false;
  }

  // [5] Check if followed by `:` (and not `::`):
  if (/^:(?!:)/.test(trimmedAfter)) {
    // If preceded by `->` (return type annotation), keep as link:
    return /(?:->)\s*$/.test(trimmedBefore);
  }

  // [6] Check if followed by single `=` (and not `==`, `!=`, `<=`, `>=`, `=>`, `=~`):
  if (/^=(?!=|[>~])/.test(trimmedAfter)) {
    // If preceded by `:` or `|` or `[` (default value in type annotation), keep as link:
    return /(?::|\||\[)\s*$/.test(trimmedBefore);
  }

  // [7] Check if untyped parameter in signature:
  if (
    /(?:^\s*|\(|,\s*|\*\s*|\*\*\s*)$/.test(trimmedBefore) &&
    /^(?:,|\)|\/|\*)/.test(trimmedAfter) &&
    !trimmedBefore.endsWith('.') &&
    !trimmedBefore.endsWith('import') &&
    !trimmedBefore.endsWith('from')
  ) {
    return /\b(?:return|yield|in|raise|is|assert|await)\s*$/.test(trimmedBefore);
  }

  return true;
}

function splitSpanText(
  spanInfo: SpanInfo,
  validMatches: RegExpMatchArray[],
  apiLinks: Record<string, string>
) {
  const spanMatches = validMatches.filter(
    (match) =>
      (match.index ?? 0) >= spanInfo.start && (match.index ?? 0) + match[0].length <= spanInfo.end
  );

  if (spanMatches.length === 0) {
    return;
  }

  const { text } = spanInfo;
  let lastIdx = 0;
  const newChildren: HastNode[] = [];

  for (const match of spanMatches) {
    const [matchedStr] = match;
    const matchStartInSpan = (match.index ?? 0) - spanInfo.start;

    if (matchStartInSpan > lastIdx) {
      newChildren.push({ type: 'text', value: text.substring(lastIdx, matchStartInSpan) });
    }

    newChildren.push({
      children: [{ type: 'text', value: matchedStr }],
      properties: { class: 'api-link', href: apiLinks[matchedStr] },
      tagName: 'a',
      type: 'element',
    });

    lastIdx = matchStartInSpan + matchedStr.length;
  }

  if (lastIdx < text.length) {
    newChildren.push({ type: 'text', value: text.substring(lastIdx) });
  }

  spanInfo.node.children = newChildren;
}

function extractSpanInfos(children: HastNode[]): { lineText: string; spanInfos: SpanInfo[] } {
  const spanInfos: SpanInfo[] = [];
  let lineText = '';

  for (const child of children) {
    if (
      child.type === 'element' &&
      child.tagName === 'span' &&
      child.children?.[0]?.type === 'text'
    ) {
      const text = child.children[0].value ?? '';
      const start = lineText.length;
      lineText += text;
      const end = lineText.length;
      spanInfos.push({ end, node: child, start, text });
    }
  }

  return { lineText, spanInfos };
}

export function apiLinkTransformer(dirname: string) {
  let apiLinks: Record<string, string> = {};
  let apiLinksPattern: RegExp | undefined = undefined;

  try {
    apiLinks = JSON.parse(fs.readFileSync(path.resolve(dirname, 'api-links.json'), 'utf8'));
    const keys = Object.keys(apiLinks).toSorted((keyA, keyB) => keyB.length - keyA.length);
    if (keys.length > 0) {
      const escapedKeys = keys.map((key) => key.replace(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`));
      apiLinksPattern = new RegExp(`\\b(${escapedKeys.join('|')})\\b`, 'g');
    }
  } catch {
    // Ignore if not present.
  }

  return {
    line(this: { options?: { lang?: string; meta?: Record<string, string> } }, node: HastNode) {
      const lang = this?.options?.lang;
      if (lang !== 'python' && lang !== 'py') {
        return;
      }

      if (!apiLinksPattern || !node.children) {
        return;
      }

      const rawMeta = this?.options?.meta?.['__raw'] || '';
      const defMatch = rawMeta.match(/def="(?<name>[^"]+)"/);
      const defName = defMatch?.groups?.name;

      const { lineText, spanInfos } = extractSpanInfos(node.children);

      const allMatches = [...lineText.matchAll(apiLinksPattern)];
      if (allMatches.length === 0) {
        return;
      }

      const validMatches = allMatches.filter((match) => shouldLinkMatch(lineText, match, defName));
      if (validMatches.length === 0) {
        return;
      }

      for (const spanInfo of spanInfos) {
        splitSpanText(spanInfo, validMatches, apiLinks);
      }
    },
    name: 'api-link-transformer',
  };
}
