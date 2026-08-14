/**
 * @name Batch File Processor
 * @description Process multiple files in batches with concurrency control and progress tracking
 * @tags automation, batch-processing, concurrency, file-operations
 */

async function processBatch(items, processor, options = {}) {
  const {
    batchSize = 5,
    onProgress = () => {},
    onError = () => {},
  } = options;

  const results = [];
  const errors = [];
  let processed = 0;

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    
    const promises = batch.map(async (item) => {
      try {
        const result = await processor(item);
        processed++;
        onProgress({ processed, total: items.length });
        return result;
      } catch (error) {
        errors.push({ item, error });
        onError(error, item);
        processed++;
        onProgress({ processed, total: items.length });
        return null;
      }
    });

    const batchResults = await Promise.all(promises);
    results.push(...batchResults.filter(r => r !== null));
  }

  return { results, errors, total: items.length };
}

// Usage:
// const files = ['file1.txt', 'file2.txt', 'file3.txt'];
// await processBatch(
//   files,
//   async (file) => await readFile(file),
//   {
//     batchSize: 2,
//     onProgress: (progress) => console.log(`${progress.processed}/${progress.total}`)
//   }
// )
