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
  let lastIndex = 0;
  const newChildren: Record<string, unknown>[] = [];
  let matched = false;

  for (const match of matches) {
    const [matchedStr] = match;
    if (matchedStr !== defName) {
      matched = true;
      const matchIndex = match.index ?? 0;
      if (matchIndex > lastIndex) {
        newChildren.push({ type: 'text', value: text.substring(lastIndex, matchIndex) });
      }
      newChildren.push({
        children: [{ type: 'text', value: matchedStr }],
        properties: { class: 'api-link', href: apiLinks[matchedStr] },
        tagName: 'a',
        type: 'element',
      });
      lastIndex = matchIndex + matchedStr.length;
    }
  }

  if (matched) {
    if (lastIndex < text.length) {
      newChildren.push({ type: 'text', value: text.substring(lastIndex) });
    }
    return newChildren;
  }
  return undefined;
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
    name: 'api-link-transformer',
    span(this: { options?: { meta?: Record<string, string> } }, node: HastNode) {
      if (
        !apiLinksPattern ||
        !node.children ||
        node.children.length !== 1 ||
        node.children[0].type !== 'text'
      ) {
        return;
      }

      const rawMeta = this?.options?.meta?.['__raw'] || '';
      const defMatch = rawMeta.match(/def="(?<name>[^"]+)"/);
      const defName = defMatch?.groups?.name;

      const text = node.children[0].value ?? '';
      const matches = [...text.matchAll(apiLinksPattern)];

      if (matches.length === 0) {
        return;
      }

      if (matches.length === 1 && matches[0][0] === text && text !== defName) {
        node.tagName = 'a';
        node.properties ||= {};
        node.properties.href = apiLinks[text];
        const existingClass = node.properties.class || '';
        node.properties.class = existingClass ? `${existingClass as string} api-link` : 'api-link';
        return;
      }

      const newChildren = splitTextIntoNodes(text, matches, defName, apiLinks);
      if (newChildren) {
        node.children = newChildren as HastNode[];
      }
    },
  };
}
