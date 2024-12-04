import os
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify
from logic.parse import parse_feature_model, parse_features
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
            logic_formulas, feature_ids = parse_feature_model(filepath)


            response = []
            for formula in logic_formulas:
                if formula.startswith("#"):
                    response.append({"constraint": formula})
                else:
                    id_to_feature = {v: k for k, v in feature_ids.items()}
                    formula_with_names = formula
                    for feature_id, feature_name in id_to_feature.items():
                        formula_with_names = formula_with_names.replace(str(feature_id), feature_name)
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

    valid = validate_xml(xml_file, xsd_schema)  # Ensure XML is valid
    if not valid:
        return jsonify({"error": "Invalid XML file"}), 400

    features, constraints = parse_features(xml_file)
    cnf, feature_ids = translate_to_cnf(features, constraints)

    is_valid, model = validate_configuration(cnf, feature_ids, selected_features, features)
    if is_valid:
        id_to_feature = {v: k for k, v in feature_ids.items()}
        configuration = {id_to_feature[abs(var)]: (var > 0) for var in model}
        selected = [feature for feature, is_selected in configuration.items() if is_selected]
        deselected = [feature for feature, is_selected in configuration.items() if not is_selected]

        return jsonify({"selected": selected, "deselected": deselected})

    return jsonify({"error": "Invalid configuration"}), 400

if __name__ == '__main__':
    app.run(debug=True)
