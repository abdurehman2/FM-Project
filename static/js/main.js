$(document).ready(function () {
  // Handle file upload
  $("#upload-form").on("submit", function (e) {
    e.preventDefault();
    const file = $("#xml-file")[0].files[0];
    if (!file) {
      alert("Please upload an XML file.");
      return;
    }

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
        if (response.constraints && response.constraints.length > 0) {
          const constraintsList = $("#constraints-list");
          constraintsList.empty(); // Clear previous constraints

          response.constraints.forEach((constraint, index) => {
            constraintsList.append(`
                <p id="constraint-${index}">
                  ${index + 1}. ${constraint.englishStatement}
                </p>
              `);
          });

          // Show the constraints section and hide upload section
          $("#constraints-section").show();
          $("#upload-section").hide();
        } else {
          alert("No cross-tree constraints found in the uploaded XML.");
        }
      },
      error: function (xhr) {
        const errorMessage =
          xhr.responseJSON?.error || "Error parsing XML file.";
        alert(errorMessage);
      },
    });
  });

  // Handle adding propositional logic
  $("#add-propositional-logic").on("click", function () {
    $("#constraints-section").hide();
    $("#propositional-section").show();

    // Generate input fields for each constraint
    const logicInputs = $("#logic-inputs");
    logicInputs.empty(); // Clear previous inputs

    $("#constraints-list p").each(function (index) {
      const constraintText = $(this).text();
      logicInputs.append(`
          <div class="mb-3">
            <label for="logic-${index}" class="form-label">
              Logic for: ${constraintText}
            </label>
            <input
              type="text"
              class="form-control"
              id="logic-${index}"
              name="logic-${index}"
              placeholder="Enter propositional logic (e.g., Location -> ByLocation)"
            />
          </div>
        `);
    });
  });

  // Handle propositional logic submission and fetch MWP
  $("#logic-form").on("submit", function (e) {
    e.preventDefault();

    const logicData = [];
    let isValid = true;

    $("#logic-form input").each(function () {
      const constraintId = $(this).attr("id");
      const logic = $(this).val().trim();

      if (!logic) {
        isValid = false;
        alert(`Please enter logic for ${constraintId}.`);
        return false; // Break the loop
      }

      const constraintIndex = constraintId.split("-")[1];
      logicData.push({
        constraintIndex: parseInt(constraintIndex, 10),
        logic,
      });
    });

    if (!isValid) return;

    // Send logic data to the backend
    $.ajax({
      url: "/process_logic_and_mwp",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ logicData }),
      success: function (response) {
        console.log("Response received:", response);

        // Display the constraints, logic, and MWP
        $("#propositional-section").hide();
        $("#mwp-section").show();

        const logicMapping = response.logicMapping || {};
        const propositionalLogic = response.propositionalLogic || [];
        const mwpConfigurations = response.mwpConfigurations || [];

        // Display Cross-Tree Constraints
        const constraintsList = $("#final-constraints-list");
        constraintsList.empty();
        propositionalLogic.forEach((constraint, index) => {
          constraintsList.append(`<li>${index + 1}. ${constraint}</li>`);
        });

        // Display Logic Mapping
        const logicList = $("#logic-list");
        logicList.empty();
        for (const key in logicMapping) {
          logicList.append(`<li>${key}: ${logicMapping[key]}</li>`);
        }

        // Display MWP Configurations
        const mwpList = $("#mwp-list");
        mwpList.empty();
        mwpConfigurations.forEach((config, index) => {
          mwpList.append(`<li>${index + 1}. ${config}</li>`);
        });
      },
      error: function (xhr) {
        alert("An error occurred while processing the request.");
      },
    });
  });

  // Restart application flow
  $("#restart").on("click", function () {
    $("#mwp-section").hide();
    $("#upload-section").show();
    $("#xml-file").val(""); // Reset the file input
  });
});
