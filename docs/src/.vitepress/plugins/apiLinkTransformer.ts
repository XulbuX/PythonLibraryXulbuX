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

function splitTextIntoNodes(
  text: string,
  matches: RegExpMatchArray[],
  defName: string | undefined,
  apiLinks: Record<string, string>
) {
  let lastIdx = 0;
  const newChildren: Record<string, unknown>[] = [];
  let matched = false;

  for (const match of matches) {
    const [matchedStr] = match;
    if (matchedStr !== defName) {
      matched = true;
      const matchIndex = match.index ?? 0;
      if (matchIndex > lastIdx) {
        newChildren.push({ type: 'text', value: text.substring(lastIdx, matchIndex) });
      }
      newChildren.push({
        children: [{ type: 'text', value: matchedStr }],
        properties: { class: 'api-link', href: apiLinks[matchedStr] },
        tagName: 'a',
        type: 'element',
      });
      lastIdx = matchIndex + matchedStr.length;
    }
  }

  if (matched) {
    if (lastIdx < text.length) {
      newChildren.push({ type: 'text', value: text.substring(lastIdx) });
    }
    return newChildren;
  }
  return undefined;
}

function isAssignmentOrKwarg(children: HastNode[], startIndex: number): boolean {
  for (let idx = startIndex + 1; idx < children.length; idx += 1) {
    const nextChild = children[idx];
    if (
      nextChild.type === 'element' &&
      nextChild.tagName === 'span' &&
      nextChild.children?.[0]?.type === 'text'
    ) {
      const nextText = nextChild.children[0].value ?? '';
      if (nextText.trim() !== '') {
        return /^=(?!=)/.test(nextText.trimStart()); // Matches `=` but not `==`, `=>`, `=~`, …
      }
    }
  }
  return false;
}

function processTokenSpan(
  child: HastNode,
  children: HastNode[],
  index: number,
  apiLinksPattern: RegExp,
  apiLinks: Record<string, string>,
  defName: string | undefined
) {
  if (
    child.type !== 'element' ||
    child.tagName !== 'span' ||
    !child.children ||
    child.children.length !== 1 ||
    child.children[0].type !== 'text'
  ) {
    return;
  }

  const text = child.children[0].value ?? '';
  const trimmed = text.trimStart();

  // [1] Skip if the text token looks like a comment or string:
  if (trimmed.startsWith('#') || /^r?f?b?["']/i.test(trimmed)) {
    return;
  }

  // [2] Skip if it's a kwarg or variable assignment (i.e. followed by `=`):
  if (isAssignmentOrKwarg(children, index)) {
    return;
  }

  const matches = [...text.matchAll(apiLinksPattern)];
  if (matches.length === 0) {
    return;
  }

  if (matches.length === 1 && matches[0][0] === text && text !== defName) {
    child.children = [
      {
        children: [{ type: 'text', value: text }],
        properties: { class: 'api-link', href: apiLinks[text] },
        tagName: 'a',
        type: 'element',
      },
    ];
    return;
  }

  const newChildren = splitTextIntoNodes(text, matches, defName, apiLinks);
  if (newChildren) {
    child.children = newChildren as HastNode[];
  }
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
    line(this: { options?: { meta?: Record<string, string> } }, node: HastNode) {
      if (!apiLinksPattern || !node.children) {
        return;
      }

      const rawMeta = this?.options?.meta?.['__raw'] || '';
      const defMatch = rawMeta.match(/def="(?<name>[^"]+)"/);
      const defName = defMatch?.groups?.name;

      for (let childIndex = 0; childIndex < node.children.length; childIndex += 1) {
        processTokenSpan(
          node.children[childIndex],
          node.children,
          childIndex,
          apiLinksPattern,
          apiLinks,
          defName
        );
      }
    },
    name: 'api-link-transformer',
  };
}
