// validation.js

// Function to validate the configuration
function validateConfiguration() {
  const selectedFeatures = window.selectedFeatures || [];

  if (selectedFeatures.length === 0) {
    $("#validation-result").html(
      '<div class="alert alert-danger">Please select at least one feature.</div>'
    );
    return;
  }

  // Get the uploaded XML file
  const xmlFile = document.getElementById("xml-file").files[0];

  if (!xmlFile) {
    $("#validation-result").html(
      '<div class="alert alert-danger">Please upload an XML file.</div>'
    );
    return;
  }

  // Create a FileReader to read the XML file content
  const reader = new FileReader();

  reader.onload = function (e) {
    const xmlContent = e.target.result; // Get the XML file content

    // Send AJAX request with the selected features and XML content
    $.ajax({
      url: "/validate",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        selected_features: selectedFeatures,
        xml_file: xmlContent, // Send the XML content here
      }),
      success: function (response) {
        $("#validation-result").html(
          '<div class="alert alert-success">Valid Configuration!</div>'
        );
      },
      error: function (xhr) {
        $("#validation-result").html(
          '<div class="alert alert-danger">' + xhr.responseJSON.error + "</div>"
        );
      },
    });
  };

  reader.onerror = function () {
    $("#validation-result").html(
      '<div class="alert alert-danger">Error reading the XML file.</div>'
    );
  };

  // Read the file content as text
  reader.readAsText(xmlFile);
}
