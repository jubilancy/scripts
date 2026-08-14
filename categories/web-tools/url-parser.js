/**
 * @name URL Query Parser
 * @description Extracts and decodes URL query string parameters into an object
 * @tags url, parsing, query-string, web
 */

function parseQuery(queryString) {
  const params = new URLSearchParams(queryString.replace(/^\?/, ''));
  const result = {};
  
  for (const [key, value] of params) {
    if (result[key]) {
      if (!Array.isArray(result[key])) {
        result[key] = [result[key]];
      }
      result[key].push(value);
    } else {
      result[key] = value;
    }
  }
  
  return result;
}

// Usage: parseQuery("?name=John&age=30&tags=js&tags=web")
// Returns: { name: "John", age: "30", tags: ["js", "web"] }
