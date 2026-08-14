/**
 * @name Retry Handler
 * @description Async retry logic with exponential backoff for failed operations
 * @tags automation, async, retry, error-handling, utilities
 */

async function retryAsync(
  fn,
  options = {}
) {
  const {
    maxAttempts = 3,
    delayMs = 1000,
    backoffMultiplier = 2,
    onRetry = () => {},
  } = options;

  let lastError;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt === maxAttempts) {
        throw error;
      }
      
      const delay = delayMs * Math.pow(backoffMultiplier, attempt - 1);
      onRetry(attempt, delay, error);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError;
}

// Usage:
// await retryAsync(
//   () => fetch('https://api.example.com/data'),
//   {
//     maxAttempts: 3,
//     delayMs: 1000,
//     backoffMultiplier: 2,
//     onRetry: (attempt, delay) => console.log(`Retry ${attempt} in ${delay}ms`)
//   }
// )
