// mwp.js

function calculateMWP() {
  const xmlFile = document.getElementById("xml-file").files[0];

  if (!xmlFile) {
    $("#mwp-result").html(
      '<div class="alert alert-danger">Please upload an XML file first.</div>'
    );
    return;
  }

  const reader = new FileReader();

  reader.onload = function (e) {
    const xmlContent = e.target.result;

    $.ajax({
      url: "/calculate_mwp",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ xml_file: xmlContent }),
      success: function (response) {
        const { mwp_configurations, count } = response;

        if (count > 0) {
          let resultHTML = `<p><strong>MWP Configurations (${count}):</strong></p><ul>`;
          mwp_configurations.forEach((config) => {
            resultHTML += `<li>${config}</li>`;
          });
          resultHTML += "</ul>";

          $("#mwp-result").html(resultHTML);
        } else {
          // No configurations found
          $("#mwp-result").html(
            '<div class="alert alert-info">No MWP configurations satisfy the constraints.</div>'
          );
        }
      },
      error: function (xhr) {
        const errorMessage = xhr.responseJSON
          ? xhr.responseJSON.error
          : "An error occurred.";
        $("#mwp-result").html(
          `<div class="alert alert-danger">${errorMessage}</div>`
        );
      },
    });
  };

  reader.onerror = function () {
    $("#mwp-result").html(
      '<div class="alert alert-danger">Error reading the XML file.</div>'
    );
  };

  // Read the file content as text
  reader.readAsText(xmlFile);
}
