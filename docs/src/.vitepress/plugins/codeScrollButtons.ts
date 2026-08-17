import { onMounted, onUnmounted } from 'vue';

function updateButtons() {
  const blocks = document.querySelectorAll('div[class*="language-"] > pre');
  for (const pre of blocks) {
    const container = pre.parentElement;
    if (container) {
      // Check if it's scrollable:
      const isScrollable = pre.scrollWidth > pre.clientWidth + 1; // +1 to prevent floating point issues.

      let leftBtn = container.querySelector('.scroll-btn-left') as HTMLButtonElement | undefined;
      let rightBtn = container.querySelector('.scroll-btn-right') as HTMLButtonElement | undefined;

      if (!isScrollable) {
        if (leftBtn) {
          leftBtn.classList.remove('visible');
        }
        if (rightBtn) {
          rightBtn.classList.remove('visible');
        }
      } else {
        if (!leftBtn) {
          leftBtn = document.createElement('button');
          leftBtn.className = 'scroll-btn-left scroll-btn';
          leftBtn.setAttribute('aria-label', 'Scroll left');
          leftBtn.innerHTML =
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>';
          container.appendChild(leftBtn);

          leftBtn.addEventListener('click', () => pre.scrollBy({ behavior: 'smooth', left: -250 }));
        }

        if (!rightBtn) {
          rightBtn = document.createElement('button');
          rightBtn.className = 'scroll-btn-right scroll-btn';
          rightBtn.setAttribute('aria-label', 'Scroll right');
          rightBtn.innerHTML =
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>';
          container.appendChild(rightBtn);

          rightBtn.addEventListener('click', () => pre.scrollBy({ behavior: 'smooth', left: 250 }));
        }

        leftBtn.classList.toggle('visible', pre.scrollLeft > 0);

        rightBtn.classList.toggle(
          'visible',
          pre.scrollLeft < pre.scrollWidth - pre.clientWidth - 1
        );
      }
    }
  }
}

function handleScroll(event: Event) {
  const target = event.target as HTMLElement;
  if (
    target &&
    target.tagName === 'PRE' &&
    target.parentElement?.matches('div[class*="language-"]')
  ) {
    const container = target.parentElement;
    const leftBtn = container.querySelector('.scroll-btn-left') as HTMLButtonElement | undefined;
    const rightBtn = container.querySelector('.scroll-btn-right') as HTMLButtonElement | undefined;

    if (leftBtn) {
      leftBtn.classList.toggle('visible', target.scrollLeft > 0);
    }
    if (rightBtn) {
      rightBtn.classList.toggle(
        'visible',
        target.scrollLeft < target.scrollWidth - target.clientWidth - 1
      );
    }
  }
}

export function setupCodeScrollButtons() {
  if (typeof globalThis.window === 'undefined') {
    return;
  }

  let observer: MutationObserver | undefined = undefined;

  onMounted(() => {
    // Initial setup:
    setTimeout(updateButtons, 100);
    globalThis.window.addEventListener('resize', updateButtons);

    // Use capture phase to catch non-bubbling scroll events on `<pre>` elements:
    document.addEventListener('scroll', handleScroll, true);

    observer = new MutationObserver((mutations) => {
      let shouldUpdate = false;
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          shouldUpdate = true;
          break;
        }
      }
      if (shouldUpdate) {
        // Small delay to allow DOM to settle and widths to be calculated:
        setTimeout(updateButtons, 50);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
  });

  onUnmounted(() => {
    globalThis.window.removeEventListener('resize', updateButtons);
    document.removeEventListener('scroll', handleScroll, true);
    if (observer) {
      observer.disconnect();
    }
  });
}
