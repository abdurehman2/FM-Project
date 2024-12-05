// upload.js

// Handle XML upload and parsing
$("#upload-form").on("submit", function (e) {
  e.preventDefault();
  const file = $("#xml-file")[0].files[0];
  const formData = new FormData();
  formData.append("xml", file);

  // Send file to server for parsing
  $.ajax({
    url: "/parse",
    type: "POST",
    data: formData,
    contentType: false,
    processData: false,
    success: function (response) {
      console.log(response); // Log the response to ensure it's correctly formatted

      // Display propositional logic
      $("#propositional-logic").html("");
      response.forEach((item) => {
        if (item.constraint) {
          $("#propositional-logic").append("<p>" + item.constraint + "</p>");
        } else {
          $("#propositional-logic").append("<p>" + item.logic_formula + "</p>");
        }
      });

      // Generate checkbox tree dynamically based on the response
      generateCheckboxTree(response);
    },
  });
});

// Generate the checkbox tree from the parsed XML response
function generateCheckboxTree(features) {
  const treeContainer = $("#checkbox-tree");
  treeContainer.html(""); // Clear previous content

  // Set to keep track of the features we've already added
  const addedFeatures = new Set();

  features.forEach((item) => {
    if (item.logic_formula) {
      const formula = item.logic_formula;

      // Extract features from the formula
      const extractedFeatures = extractFeaturesFromFormula(formula);

      extractedFeatures.forEach((feature) => {
        if (!addedFeatures.has(feature)) {
          addedFeatures.add(feature);

          // Generate the checkbox HTML
          const checkbox = `<div class="form-check">
            <input type="checkbox" class="form-check-input" id="${feature}" onchange="updateSelectedFeatures()">
            <label class="form-check-label" for="${feature}">${feature}</label>
          </div>`;

          // Append the checkbox to the tree container
          treeContainer.append(checkbox);
        }
      });
    }
  });
}

// Extract unique feature names from the logic formula
function extractFeaturesFromFormula(formula) {
  const regex = /[A-Za-z0-9_]+/g; // Matches words consisting of letters, numbers, and underscores
  return formula.match(regex) || []; // Return matched features or an empty array
}

// Function to handle the selection of checkboxes (optional)
function updateSelectedFeatures() {
  const selectedFeatures = [];
  $(".form-check-input:checked").each(function () {
    selectedFeatures.push(this.id);
  });
  console.log("Selected Features:", selectedFeatures);
}
