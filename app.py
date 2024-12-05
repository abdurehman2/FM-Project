import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from logic.parse import parse_feature_model, parse_feature_model2
from logic.validate import validate_configuration
from logic.translate import translate_to_cnf
from logic.xmlvalidate import validate_xml

app = Flask(__name__)

xsd_schema = 'logic/feature-model.xsd'

@app.route('/')
def index():
    return render_template('index.html')

# Configure the folder for saving uploaded files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xml'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/parse', methods=['POST'])
def parse_xml():
    # Check if a file was uploaded
    if 'xml' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['xml']

    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Ensure the file has a valid extension
    if file and allowed_file(file.filename):
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Parse the uploaded XML file
        try:
            logic_formulas= parse_feature_model(filepath)


            response = []
            for formula in logic_formulas:
                if formula.startswith("#"):
                    response.append({"constraint": formula})
                else:
                    formula_with_names = formula
                    response.append({"logic_formula": formula_with_names})
                    

            return jsonify(response)
        except Exception as e:
            return jsonify({"error": f"Error parsing XML: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file format. Only XML files are allowed."}), 400



@app.route('/validate', methods=['POST'])
def validate_config():
    data = request.get_json()
    selected_features = data.get('selected_features', [])
    xml_file = data.get('xml_file')

    # Step 1: Validate the XML schema (using XSD schema)
    valid = validate_xml(xml_file, xsd_schema)
    if not valid:
        return jsonify({"error": "Invalid XML file"}), 400

    # Step 2: Parse the feature model from XML using the new parse_feature_model2 function
    features, validate_feature_selection, visualize_feature_model = parse_feature_model2(xml_file)

    # Step 3: Visualize the feature model (send it to frontend for rendering)
    feature_tree = visualize_feature_model(features)

    # Step 4: Validate the selected configuration dynamically
    validation_result = {"valid": True, "errors": []}

    # Validate the selected features based on the constraints
    for feature in selected_features:
        # If a feature is selected, validate it
        if feature in features:
            validate_feature_selection(feature, True)
        else:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Feature {feature} not found in the model.")

    if validation_result["valid"]:
        # Return the feature tree and validation result to frontend
        return jsonify({
            "feature_tree": feature_tree,
            "validation": validation_result,
            "selected": selected_features,
        })

    return jsonify({"error": "Invalid configuration based on constraints", "details": validation_result}), 400


if __name__ == '__main__':
    app.run(debug=True)
