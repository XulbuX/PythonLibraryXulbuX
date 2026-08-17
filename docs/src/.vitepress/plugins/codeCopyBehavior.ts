import { onMounted, onUnmounted } from 'vue';

function handleCopy(event: ClipboardEvent) {
  const selection = globalThis.getSelection();
  if (!selection || selection.isCollapsed || !event.clipboardData) {
    return;
  }

  // Check if the selection intersects with a code block:
  const range = selection.getRangeAt(0);
  let node: Node | null = range.commonAncestorContainer;
  let inCodeBlock = false;

  // Find if the common ancestor is inside a VitePress code block:
  while (node && node !== document.body) {
    if (
      node instanceof Element &&
      (node.matches('[class*="language-"]') || node.closest('[class*="language-"]'))
    ) {
      inCodeBlock = true;
      break;
    }
    node = node.parentNode;
  }

  if (inCodeBlock) {
    // Force plain text copy to strip out hyperlink formatting and preserve pure code:
    event.clipboardData.setData('text/plain', selection.toString());
    event.preventDefault();
  }
}

export function setupCodeCopyBehavior() {
  if (typeof globalThis.window === 'undefined') {
    return;
  }

  onMounted(() => document.addEventListener('copy', handleCopy));
  onUnmounted(() => document.removeEventListener('copy', handleCopy));
}
