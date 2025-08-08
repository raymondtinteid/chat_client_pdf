// Field configurations for different products
const fieldConfigs = {
  RCN: {
    productInfo: [
      { label: "Underlying Asset", name: "underlyingAsset", type: "text", defaultValue: "Vodafone Group PLC Bond" },
      { label: "Currency", name: "currency", type: "text", defaultValue: "GBP" },
      { label: "Face Value", name: "faceValue", type: "text", defaultValue: "10,000,000" },
      { label: "Ask Price", name: "askPrice", type: "text", defaultValue: "108.714" },
      { label: "Coupon Rate (p.a.)", name: "couponRate", type: "text", defaultValue: "8.00%" },
      { label: "Next Call Date", name: "nextCallDate", type: "text", defaultValue: "30/05/2031" },
      { label: "Call Price", name: "callPrice", type: "text", defaultValue: "100.00" },
      { label: "Ask Yield to Worst (YTW)", name: "askYieldToWorst", type: "text", defaultValue: 6.2 }
    ],
    fundingOptions: [
      { label: "Funding Currency", name: "fundingCurrency", type: "text", defaultValue: "USD" },
      { label: "Spot Rate", name: "spotRate", type: "text", defaultValue: "1.3600" },
      { label: "Lombard Loan Interest Rate (p.a.)", name: "lombardLoanInterestRate", type: "text", defaultValue: "5%" },
      { label: "Investment Lending Value", name: "investmentLendingValue", type: "text", defaultValue: "75%" }
    ],
    fundingSituation: [
      { label: "Available Cash Liquidity", name: "availableCashLiquidity", type: "text", defaultValue: "USD 5,000,000" },
      { label: "Total Approved Credit Limit", name: "totalApprovedCreditLimit", type: "text", defaultValue: "USD 25,000,000" },
      { label: "Current Lombard Loan Exposure", name: "currentLombardLoanExposure", type: "text" }
    ]
  },
  Bond: {
    productInfo: [
      { label: "Ask Price", name: "askPrice", type: "text" },
      { label: "Next Call Date", name: "nextCallDate", type: "text" },
      { label: "Call Price", name: "callPrice", type: "text" },
      { label: "Ask Yield to Worst", name: "askYieldToWorst", type: "text" }
    ],
    fundingOptions: [
      { label: "Funding Currency", name: "fundingCurrency", type: "text", defaultValue: "USD" },
      { label: "Spot Rate", name: "spotRate", type: "text" },
      { label: "Lombard Loan Interest Rate (p.a.)", name: "lombardLoanInterestRate", type: "text", defaultValue: "5%" },
      { label: "Investment Lending Value", name: "investmentLendingValue", type: "text" }
    ],
    fundingSituation: [
      { label: "Available Cash Liquidity", name: "availableCashLiquidity", type: "text" },
      { label: "Total Approved Credit Limit", name: "totalApprovedCreditLimit", type: "text" },
      { label: "Current Lombard Loan Exposure", name: "currentLombardLoanExposure", type: "text" }
    ]
  }
};

// Prompt field configuration with default values
const promptFields = [
  { label: "Introduction", name: "introduction", defaultValue: "this is the intro" },
  { label: "Part A: Pre-Calculation & Analysis", name: "partA" },
  { label: "Part B: The Funding Options", name: "partB" },
  { label: "Part C: Scenario Analysis", name: "partC" },
  { label: "Part D: FX Sensitivity Analysis", name: "partD", defaultValue: "this is part d" },
  { label: "Part E: Full Narrative Generation", name: "partE", defaultValue: "this is part e" }
];

let currentProduct = 'RCN';
let productInfoFields = fieldConfigs[currentProduct].productInfo;
let fundingOptionsFields = fieldConfigs[currentProduct].fundingOptions;
let fundingSituationFields = fieldConfigs[currentProduct].fundingSituation;
const values = {};
const promptValues = {};

// Render fields for a specific subsection
function renderFieldsInContainer(fields, containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  fields.forEach(field => {
    const group = document.createElement('div');
    group.className = '';
    group.innerHTML = `
      <label class="block text-base font-semibold text-primary mb-2" for="${field.name}">${field.label}</label>
      <input 
        type="${field.type}" 
        id="${field.name}" 
        name="${field.name}" 
        value="${values[field.name] || field.defaultValue || ''}" 
        autocomplete="off"
        class="rounded-lg border border-primary bg-card text-primary px-4 py-3 focus:ring-2 focus:ring-focus focus:border-focus transition-all duration-200 shadow-md w-full placeholder:text-primary/60"
        placeholder="${field.label}"
      />
    `;
    container.appendChild(group);

    // Set default value if it exists and field is empty
    if (field.defaultValue && !values[field.name]) {
      values[field.name] = field.defaultValue;
    }

    // Listen for changes
    group.querySelector('input').addEventListener('input', (e) => {
      values[field.name] = e.target.value;
      updatePrompts();
    });
  });
}

// Render all input fields
function renderInputFields() {
  renderFieldsInContainer(productInfoFields, 'product-info-grid');
  renderFieldsInContainer(fundingOptionsFields, 'funding-options-grid');
  renderFieldsInContainer(fundingSituationFields, 'funding-grid');
}

/**
 * Render prompt fields as collapsible, non-editable, normal-font blocks.
 */
function renderPromptFields() {
  const container = document.getElementById('prompts-grid');
  container.innerHTML = '';
  promptFields.forEach(promptField => {
    const group = document.createElement('div');
    group.className = 'relative flex flex-col gap-2 w-full';

    // Get the initial value - either stored value or default value
    const initialValue = promptValues[promptField.name] || promptField.defaultValue || '';

    // Collapsible details/summary with copy button and normal font
    group.innerHTML = `
      <label class="block text-base font-semibold text-primary mb-1" for="${promptField.name}">${promptField.label}</label>
      <div class="relative w-full">
        <button type="button" class="absolute top-2 right-2 z-10 bg-gold text-primary font-bold py-1 px-4 rounded-lg shadow-md text-xs hover:scale-105 hover:bg-accent hover:text-white transition-all duration-150 copy-btn" onclick="copyPrompt('${promptField.name}')">Copy</button>
        <details open class="w-full">
          <summary class="cursor-pointer select-none text-primary font-medium text-sm py-1 px-2 rounded hover:bg-accent/10 transition-all duration-150">Show/Hide</summary>
          <div 
            id="${promptField.name}" 
            name="${promptField.name}"
            class="prompt-block font-sans text-base bg-surface border border-gold/30 rounded-xl min-h-[80px] w-full box-border p-4 whitespace-pre-wrap break-words mt-2 outline-none text-primary shadow-inner"
            tabindex="0"
          >${initialValue}</div>
        </details>
      </div>
    `;
    container.appendChild(group);

    // Set the initial value in promptValues if not already set
    if (!promptValues[promptField.name] && promptField.defaultValue) {
      promptValues[promptField.name] = promptField.defaultValue;
    }
  });
}

function getAssumptionsString() {
  let productInfoList = productInfoFields.map(field =>
    `${field.label}: ${values[field.name] || ''}`
  );
  let fundingOptionsList = fundingOptionsFields.map(field =>
    `${field.label}: ${values[field.name] || ''}`
  );
  let fundingList = fundingSituationFields.map(field =>
    `${field.label}: ${values[field.name] || ''}`
  );
  
  return `These are the assumptions:
Product: ${currentProduct}

Product Information:
${productInfoList.join('\n')}

Funding Options:
${fundingOptionsList.join('\n')}

C assumptions:
${fundingList.join('\n')}`;
}

function getFundingOptionsString() {
  let fundingOptionsList = fundingOptionsFields.map(field =>
    `${field.label}: ${values[field.name] || ''}`
  );
  return `These are the Funding Options:\n${fundingOptionsList.join('\n')}`;
}

function getCAssumptionsString() {
  let fundingList = fundingSituationFields.map(field =>
    `${field.label}: ${values[field.name] || ''}`
  );
  return `These are the C info assumptions:\n${fundingList.join('\n')}`;
}

/**
 * Update all prompts with their respective content
 * (now updates the textContent of the prompt-block divs)
 */
function updatePrompts() {
  updatePartA();
  updatePartB();
  updatePartC();
}

// Update Part A with current assumptions
function updatePartA() {
  const partABlock = document.getElementById('partA');
  if (partABlock) {
    const assumptionsText = getAssumptionsString();
    partABlock.textContent = assumptionsText;
    promptValues['partA'] = assumptionsText;
  }
}

// Update Part B with funding options
function updatePartB() {
  const partBBlock = document.getElementById('partB');
  if (partBBlock) {
    const fundingOptionsText = getFundingOptionsString();
    partBBlock.textContent = fundingOptionsText;
    promptValues['partB'] = fundingOptionsText;
  }
}

// Update Part C with C assumptions
function updatePartC() {
  const partCBlock = document.getElementById('partC');
  if (partCBlock) {
    const cAssumptionsText = getCAssumptionsString();
    partCBlock.textContent = cAssumptionsText;
    promptValues['partC'] = cAssumptionsText;
  }
}

// Handle product change
function handleProductChange(newProduct) {
  currentProduct = newProduct;
  productInfoFields = fieldConfigs[currentProduct].productInfo;
  fundingOptionsFields = fieldConfigs[currentProduct].fundingOptions;
  fundingSituationFields = fieldConfigs[currentProduct].fundingSituation;
  
  // Get all field names from new product config
  const allNewFieldNames = [
    ...productInfoFields.map(f => f.name),
    ...fundingOptionsFields.map(f => f.name),
    ...fundingSituationFields.map(f => f.name)
  ];
  
  // Clear values that don't exist in new product
  Object.keys(values).forEach(key => {
    if (!allNewFieldNames.includes(key)) {
      delete values[key];
    }
  });
  
  // Initialize new fields with default values
  [...productInfoFields, ...fundingOptionsFields, ...fundingSituationFields].forEach(f => {
    if (!(f.name in values)) {
      values[f.name] = f.defaultValue || '';
    }
  });
  
  renderInputFields();
  updatePrompts();
}

/**
 * Copy to clipboard function for prompts (now copies from div, not textarea)
 */
function copyPrompt(promptName) {
  const block = document.getElementById(promptName);
  if (!block) return;
  // Create a temporary textarea to copy the text content
  const temp = document.createElement('textarea');
  temp.value = block.textContent;
  document.body.appendChild(temp);
  temp.select();
  document.execCommand('copy');
  document.body.removeChild(temp);

  // Visual feedback
// Find the copy button in the current prompt group
  const copyBtn = block.parentElement.parentElement.querySelector('.copy-btn');
  if (copyBtn) {
    copyBtn.textContent = 'Copied!';
    setTimeout(() => copyBtn.textContent = 'Copy', 1000);
  }
}

// Make copyPrompt available globally for onclick handlers
window.copyPrompt = copyPrompt;

// Save current state to HTML file
function saveCurrentState() {
  const saveBtn = document.getElementById('save-btn');
  saveBtn.disabled = true;
  saveBtn.textContent = 'Saving...';
  
  try {
    // Clone the current document
    const docClone = document.documentElement.cloneNode(true);
    
    // Remove the save section from the clone to avoid recursive save buttons
    const saveSection = docClone.querySelector('#save-section');
    if (saveSection) {
      saveSection.remove();
    }
    
    // Remove script tag to create a static version
    const scriptTags = docClone.querySelectorAll('script');
    scriptTags.forEach(script => script.remove());
    
    // Update all input values in the clone with current values
    Object.keys(values).forEach(key => {
      const input = docClone.querySelector(`#${key}`);
      if (input) {
        input.setAttribute('value', values[key] || '');
      }
    });
    
    // Update all textarea values in the clone with current values
    Object.keys(promptValues).forEach(key => {
      const textarea = docClone.querySelector(`#${key}`);
      if (textarea) {
        textarea.textContent = promptValues[key] || '';
      }
    });
    
    // Update select value in the clone
    const select = docClone.querySelector('#product');
    if (select) {
      const options = select.querySelectorAll('option');
      options.forEach(option => {
        if (option.value === currentProduct) {
          option.setAttribute('selected', 'selected');
        } else {
          option.removeAttribute('selected');
        }
      });
    }
    
    // Create the complete HTML
    const htmlContent = '<!DOCTYPE html>\n' + docClone.outerHTML;
    
    // Create and download the file
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `assumption-form-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Reset button
    saveBtn.textContent = 'Saved!';
    setTimeout(() => {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Current State to Disk';
    }, 2000);
    
  } catch (error) {
    console.error('Error saving file:', error);
    saveBtn.textContent = 'Error saving';
    setTimeout(() => {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Current State to Disk';
    }, 2000);
  }
}

// Initialization
function init() {
  // Initialize values for current product with defaults
  [...productInfoFields, ...fundingOptionsFields, ...fundingSituationFields].forEach(f => {
    if (!(f.name in values)) {
      values[f.name] = f.defaultValue || '';
    }
  });

  // Initialize prompt values with defaults
  promptFields.forEach(f => {
    if (!(f.name in promptValues)) {
      promptValues[f.name] = f.defaultValue || '';
    }
  });
  
  renderInputFields();
  renderPromptFields();
  updatePrompts(); // This will populate Part A, B, and C
  
  // Product dropdown listener
  document.getElementById('product').addEventListener('change', (e) => {
    handleProductChange(e.target.value);
  });
  
  // Save button listener
  document.getElementById('save-btn').addEventListener('click', saveCurrentState);
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', init);

// To extend: 
// 1. Add new products to fieldConfigs object with productInfo, fundingOptions, and fundingSituation arrays
// 2. Add new options to the product dropdown in HTML
// 3. Add new prompt fields to promptFields array with optional defaultValue
// 4. System adapts automatically
