export const debounce = <F extends (...args: any[]) => any>(fn: F, ms = 300) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  const debounced = function (this: any, ...args: Parameters<F>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), ms);
  };
  debounced.cancel = () => clearTimeout(timeoutId);
  return debounced;
};