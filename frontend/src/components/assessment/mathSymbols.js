/** Nepal CDC maths & science symbol palettes (LaTeX snippets). */

export const MATH_SYMBOL_GROUPS = [
  {
    label: "Basic",
    symbols: [
      { label: "+", insert: " + ", title: "Plus" },
      { label: "−", insert: " - ", title: "Minus" },
      { label: "×", insert: " \\times ", title: "Multiply" },
      { label: "÷", insert: " \\div ", title: "Divide" },
      { label: "=", insert: " = ", title: "Equals" },
      { label: "≠", insert: " \\neq ", title: "Not equal" },
      { label: "≈", insert: " \\approx ", title: "Approximately" },
      { label: "±", insert: " \\pm ", title: "Plus minus" },
    ],
  },
  {
    label: "Powers & roots",
    symbols: [
      { label: "x²", insert: "x^{2}", title: "Square" },
      { label: "x³", insert: "x^{3}", title: "Cube" },
      { label: "xⁿ", insert: "x^{n}", title: "Power n" },
      { label: "√", insert: "\\sqrt{}", title: "Square root", cursorOffset: -1 },
      { label: "∛", insert: "\\sqrt[3]{}", title: "Cube root", cursorOffset: -1 },
      { label: "ⁿ√", insert: "\\sqrt[n]{}", title: "nth root", cursorOffset: -1 },
      { label: "a/b", insert: "\\frac{}{}", title: "Fraction", cursorOffset: -3 },
    ],
  },
  {
    label: "Functions",
    symbols: [
      { label: "sin", insert: "\\sin", title: "Sine" },
      { label: "cos", insert: "\\cos", title: "Cosine" },
      { label: "tan", insert: "\\tan", title: "Tangent" },
      { label: "log", insert: "\\log", title: "Logarithm" },
      { label: "ln", insert: "\\ln", title: "Natural log" },
      { label: "lim", insert: "\\lim_{x \\to }", title: "Limit", cursorOffset: -1 },
    ],
  },
  {
    label: "Greek & constants",
    symbols: [
      { label: "π", insert: "\\pi", title: "Pi" },
      { label: "θ", insert: "\\theta", title: "Theta" },
      { label: "α", insert: "\\alpha", title: "Alpha" },
      { label: "β", insert: "\\beta", title: "Beta" },
      { label: "Δ", insert: "\\Delta", title: "Delta" },
      { label: "∞", insert: "\\infty", title: "Infinity" },
      { label: "°", insert: "^{\\circ}", title: "Degrees" },
    ],
  },
  {
    label: "Sets & logic",
    symbols: [
      { label: "∈", insert: "\\in", title: "Element of" },
      { label: "∪", insert: "\\cup", title: "Union" },
      { label: "∩", insert: "\\cap", title: "Intersection" },
      { label: "⊂", insert: "\\subset", title: "Subset" },
      { label: "A×B", insert: "A \\times B", title: "Cartesian product" },
      { label: "n(A)", insert: "n(A)", title: "Cardinality" },
      { label: "≤", insert: "\\leq", title: "Less or equal" },
      { label: "≥", insert: "\\geq", title: "Greater or equal" },
    ],
  },
  {
    label: "Nepal context",
    symbols: [
      { label: "Rs.", insert: "\\text{Rs.}", title: "Nepali Rupees" },
      { label: "%", insert: "\\%", title: "Percent" },
      { label: "cm", insert: "\\text{ cm}", title: "Centimetres" },
      { label: "m", insert: "\\text{ m}", title: "Metres" },
      { label: "km", insert: "\\text{ km}", title: "Kilometres" },
      { label: "kg", insert: "\\text{ kg}", title: "Kilograms" },
    ],
  },
];

export const SCIENCE_SYMBOL_GROUPS = [
  {
    label: "Science",
    symbols: [
      { label: "→", insert: "\\rightarrow", title: "Yields" },
      { label: "⇌", insert: "\\rightleftharpoons", title: "Reversible" },
      { label: "Δ", insert: "\\Delta", title: "Change" },
      { label: "H₂O", insert: "H_2O", title: "Subscript example" },
      { label: "CO₂", insert: "CO_2", title: "Carbon dioxide" },
      { label: "°C", insert: "^{\\circ}\\text{C}", title: "Celsius" },
      { label: "μ", insert: "\\mu", title: "Micro" },
      { label: "λ", insert: "\\lambda", title: "Wavelength" },
      { label: "Ω", insert: "\\Omega", title: "Ohm" },
      { label: "F=ma", insert: "F = ma", title: "Newton's law" },
      { label: "V=IR", insert: "V = IR", title: "Ohm's law" },
      { label: "Q=mcΔT", insert: "Q = mc\\Delta T", title: "Heat equation" },
    ],
  },
  ...MATH_SYMBOL_GROUPS.slice(0, 4),
];

export function getSymbolGroups(subject) {
  const s = (subject || "").toLowerCase();
  return s === "science" ? SCIENCE_SYMBOL_GROUPS : MATH_SYMBOL_GROUPS;
}
