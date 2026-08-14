/**
 * @name Hex to RGB Converter
 * @description Converts hexadecimal color codes to RGB format
 * @tags color, conversion, hex, rgb, formatting
 */

function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
    toString() {
      return `rgb(${this.r}, ${this.g}, ${this.b})`;
    }
  } : null;
}

function rgbToHex(r, g, b) {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase();
}

// Usage: 
// hexToRgb("#FF5733") → { r: 255, g: 87, b: 51, toString: [Function] }
// rgbToHex(255, 87, 51) → "#FF5733"
