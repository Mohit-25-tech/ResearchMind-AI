/**
 * Animates text appearing character-by-character.
 *
 * @param fullText    The complete text to type out
 * @param onUpdate    Called with the current visible substring on each tick
 * @param onComplete  Called when the full text has been typed
 * @param speed       Milliseconds per character (default 12ms)
 * @returns A cancel function to abort the animation early
 */
export function startTypingAnimation(
  fullText: string,
  onUpdate: (visibleText: string) => void,
  onComplete: () => void,
  speed: number = 12,
): () => void {
  let index = 0;
  let cancelled = false;

  function tick() {
    if (cancelled) return;

    // Type in chunks of 2-4 characters for a more natural feel
    const chunkSize = Math.min(
      Math.floor(Math.random() * 3) + 2,
      fullText.length - index,
    );
    index += chunkSize;

    onUpdate(fullText.slice(0, index));

    if (index >= fullText.length) {
      onComplete();
    } else {
      setTimeout(tick, speed);
    }
  }

  // Start the first tick
  setTimeout(tick, speed);

  return () => {
    cancelled = true;
  };
}
