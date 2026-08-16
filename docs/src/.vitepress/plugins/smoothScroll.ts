import { inBrowser, onContentUpdated } from 'vitepress';
import { ref, onUnmounted } from 'vue';

interface SmoothScrollOptions {
  /** Duration in milliseconds (lower = faster). */
  duration?: number;
  /** Pixel offset from target (useful for fixed headers). */
  offset?: number;
  /** Custom easing function. */
  easing?: (
    elapsedTime: number,
    startValue: number,
    changeInValue: number,
    totalDuration: number
  ) => number;
}

function easeInOutQuart(
  elapsedTime: number,
  startValue: number,
  changeInValue: number,
  totalDuration: number
): number {
  let normTime = elapsedTime / (totalDuration / 2);
  if (normTime < 1) {
    return (changeInValue / 2) * normTime * normTime * normTime * normTime + startValue;
  }
  normTime -= 2;
  return (-changeInValue / 2) * (normTime * normTime * normTime * normTime - 2) + startValue;
}

function useSmoothScroll() {
  let rafId: number | undefined = undefined;
  const isScrolling = ref(false);

  function cancelScroll(): void {
    if (rafId !== undefined) {
      cancelAnimationFrame(rafId);
      rafId = undefined;
    }
    isScrolling.value = false;
  }

  function scrollTo(
    target: string | HTMLElement | number,
    options: SmoothScrollOptions = {}
  ): Promise<void> {
    cancelScroll();

    return new Promise((resolve) => {
      let targetY = 0,
        startTime: number | undefined = undefined;

      const { duration = 400, offset = 0, easing = easeInOutQuart } = options;

      if (typeof target === 'number') {
        targetY = target;
      } else if (typeof target === 'string') {
        const targetElement = document.querySelector<HTMLElement>(target);
        if (!targetElement) {
          resolve();
          return;
        }
        targetY = targetElement.getBoundingClientRect().top + window.scrollY;
      } else if (target instanceof HTMLElement) {
        targetY = target.getBoundingClientRect().top + window.scrollY;
      }

      targetY += offset;
      const startY = window.scrollY,
        distance = targetY - startY;

      if (Math.abs(distance) < 1 || duration <= 0) {
        window.scrollTo(0, targetY);
        resolve();
        return;
      }

      isScrolling.value = true;

      function step(currentTime: number): void {
        if (startTime === undefined) {
          startTime = currentTime;
        }
        const elapsed = currentTime - startTime,
          progress = Math.min(elapsed, duration),
          nextY = easing(progress, startY, distance, duration);

        window.scrollTo(0, nextY);

        if (elapsed < duration) {
          rafId = requestAnimationFrame(step);
        } else {
          window.scrollTo(0, targetY);
          isScrolling.value = false;
          rafId = undefined;
          resolve();
        }
      }

      rafId = requestAnimationFrame(step);
    });
  }

  onUnmounted(() => cancelScroll());

  return { cancelScroll, isScrolling, scrollTo };
}

export function setupSmoothScroll() {
  const { scrollTo } = useSmoothScroll();

  if (inBrowser) {
    onContentUpdated(() => {
      const { hash } = globalThis.location;
      if (hash && hash.length > 1) {
        setTimeout(() => {
          const el = document.getElementById(hash.slice(1));
          if (el) {
            const navbar = document.querySelector('.VPNav') as HTMLElement;
            const offset = navbar ? navbar.offsetHeight : 64;
            const padding = 32;

            scrollTo(el, { duration: 0, offset: -(offset + padding) }).then(() => {
              el.classList.add('target-highlight');
              setTimeout(() => {
                el.classList.remove('target-highlight');
              }, 1500);
            });
          }
        }, 100);
      }
    });

    document.addEventListener('click', (event) => {
      const target = (event.target as HTMLElement).closest('a');
      if (target) {
        const href = target.getAttribute('href');
        if (href) {
          try {
            const url = new URL(href, globalThis.location.href);
            if (url.pathname === globalThis.location.pathname && url.hash.length > 1) {
              const el = document.getElementById(url.hash.slice(1));
              if (el) {
                event.preventDefault();
                const navbar = document.querySelector('.VPNav') as HTMLElement;
                const offset = navbar ? navbar.offsetHeight : 64;
                const padding = 32;

                scrollTo(el, { duration: 500, offset: -(offset + padding) }).then(() => {
                  history.pushState(undefined, '', url.hash);
                  el.classList.add('target-highlight');
                  setTimeout(() => {
                    el.classList.remove('target-highlight');
                  }, 1500);
                });
              }
            }
          } catch {
            // Ignore invalid URLs.
          }
        }
      }
    });
  }
}
