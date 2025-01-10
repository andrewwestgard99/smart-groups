from flask import Flask, render_template_string, request, redirect, url_for
import re
app = Flask(__name__)

# In-memory storage for smart groups
smart_groups = []

# List of available criteria
criteria_list = [
"Activation Lock Enabled", "AirPlay Password", "App Analytics Enabled", "App Identifier", "App Name", "App Short Version", "App Validation Status", "App Version", "AppleCare ID", "Apps Installed Match the App Catalog Exactly", "Apps Not In the App Catalog Are Installed", "Asset Tag", "Attestation Status", "Available Space MB", "Battery Health", "Battery Level", "BeyondCorp Enterprise Integration - Compliance Status", "BeyondCorp Enterprise Integration - Registration Status", "Block Encryption Capability", "Bluetooth Low Energy Capability", "Bluetooth MAC Address", "Building", "Capacity MB", "Carrier Settings Version", "Cellular Technology", "Certificate Issuer", "Certificate Name", "Certificates Expiring", "Current Carrier Network", "Current Mobile Country Code", "Current Mobile Network Code", "Data Protection", "Data Roaming Enabled", "Date Lost Mode Enabled", "Declarative Device Management Enabled", "Department", "Device Compliance Integration - Compliance Status", "Device Compliance Integration - Registration Status", "Device ID", "Device Locator Service Enabled", "Device Ownership Type", "Device Phone Number", "Diagnostic and Usage Reporting Enabled", "Display Name", "Do Not Disturb Enabled", "eBook Title", "eBook Version", "EID", "Email Address", "Enrollment Method: Enrollment profile", "Enrollment Method: PreStage enrollment", "Enrollment Method: User-initiated - invitation", "Enrollment Method: User-initiated - no invitation", "Enrollment Session Token Valid", "Exchange Device ID", "Expires", "File Encryption Capability", "Full Name", "Hardware Encryption", "Home Carrier Network", "Home Mobile Country Code", "Home Mobile Network Code", "ICCID", "iCloud Backup Enabled", "Identifier", "Identity", "IMEI", "IMEI2", "IP Address", "iTunes Store Account", "Jailbreak Detected", "Jamf Parent Pairings", "JSS Mobile Device ID", "Languages", "Last Attestation Attempt", "Last Backup", "Last Enrollment", "Last iCloud Backup", "Last Inventory Update", "Last Successful Attestation", "Lease Expiration", "Life Expectancy", "Locales", "Location Services for Self Service Mobile", "Lost Mode Enabled", "MDM Profile Expiration Date", "MDM Profile Removal Allowed", "MDM Profile Renewal Needed - CA Renewed", "MEID", "Mobile Device Group", "Model", "Model Identifier", "Model Number", "Modem Firmware Version", "OS Build", "OS Rapid Security Response", "OS Version", "Passcode Compliance", "Passcode Compliance with Profile(s)", "Passcode Lock Grace Period Enforced (seconds)", "Passcode Status", "Personal Hotspot Enabled", "PO Date", "PO Number", "Position", "Profile Name", "Provisioning Profile Name", "Purchase Price", "Purchased or Leased", "Purchasing Account", "Purchasing Contact", "Storage Quota Size", "Number of Users", "Roaming", "Room", "Serial Number", "Shared iPad", "Software Update Device ID", "Supervised", "Tethered", "Time Zone", "UDID", "Used Space Percentage", "User Phone Number", "Username", "Vendor", "Version", "Voice Roaming Enabled", "Warranty Expiration", "Wi-Fi MAC Addres" 
]

@app.route('/')
def smart_computer_groups_dashboard():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Smart Computer Groups</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    </head>
    <body>
        <div class="sidebar">
            <h2>Computers</h2>
            <a href="#">Inventory</a>
            <a href="#">Search Inventory</a>
            <a href="#">Search Volume Content</a>
            <a href="#">Licensed Software</a>
            <h2>Groups</h2>
            <a href="/">Smart Computer Groups</a>
            <a href="#">Static Computer Groups</a>
            <a href="#">Classes</a>
        </div>
        <div class="content">
            <div class="dashboard-header">
                <h1>Smart Computer Groups</h1>
            </div>
            <p>Smart computer groups allow you to dynamically organize and manage devices based on specific criteria or attributes. The advantage of Smart Groups is that they are dynamic and automatically update as devices meet or no longer meet the specified criteria. This automation makes it easier to maintain and manage devices without manual intervention. </p>
            <br><br><br>
            <div class="new">
            <button onclick="window.location.href='/new-smart-group'">+ New Smart Group</button>
            </div>
            <br><br><br>
            <div class="dashboard-content">
                {% if smart_groups %}
                    {% for group in smart_groups %}
                        <div class="card">
                            <h2>{{ group['name'] }}</h2>
                            <p>Enabled: {{ group['isEnabled'] }}</p>
                            <p>Criteria: {{ group['criteria'] }}</p>
                            <div class="actions">
                                <button class="card-button" onclick="window.location.href='/edit-smart-group/{{ loop.index0 }}'">View/Edit</button>
                                <button class="card-button" onclick="alert('Previewing Computers...')">Preview Computers</button>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p></p>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    ''', smart_groups=smart_groups)

@app.route('/new-smart-group', methods=['GET', 'POST'])
def new_smart_computer_group():
    if request.method == 'POST':
        name = request.form['name']
        isEnabled = 'isEnabled' in request.form
        description = request.form['description']

        def parse_criteria_group(form_data, prefix=''):
            criteria = []
            index = 0
            while f'{prefix}criteria[{index}][type]' in form_data or f'{prefix}criteria[{index}][isGroup]' in form_data:
                crit_data = {}
                
                if f'{prefix}criteria[{index}][isGroup]' in form_data:
                    crit_data = {
                        "isGroup": True,
                        "criteria": parse_criteria_group(form_data, f'{prefix}criteria[{index}].'),
                        "logical_operator": None
                    }
                    if index > 0:
                        crit_data["logical_operator"] = form_data.get(f'{prefix}criteria[logical][{index - 1}]', 'AND')
                else:
                    crit_data = {
                        "isGroup": False,
                        "type": form_data.get(f'{prefix}criteria[{index}][type]'),
                        "operator": form_data.get(f'{prefix}criteria[{index}][operator]'),
                        "value": form_data.get(f'{prefix}criteria[{index}][value]'),
                        "logical_operator": form_data.get(f'{prefix}criteria[logical][{index - 1}]', 'AND') if index > 0 else None
                    }

                criteria.append(crit_data)
                index += 1
            return criteria

        # Wrap the parsed criteria in a root group
        parsed_criteria = parse_criteria_group(request.form)
        root_group = {
            "isGroup": True,
            "criteria": parsed_criteria,
            "logical_operator": None
        }

        smart_groups.append({
            'name': name,
            'description': description,
            'isEnabled': isEnabled,
            'criteria': [root_group]  # Store as array with single root group
        })
        return redirect(url_for('smart_computer_groups_dashboard'))

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Smart Computer Group</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.15.0/Sortable.min.js"></script>
    <script>
        let criteriaIndex = 1;

        function addCriteria(container = null) {
            const builder = container || document.getElementById('criteriaBuilder');
            
            // Create a wrapper div to hold both logical operator and criteria row
            const wrapper = document.createElement('div');
            wrapper.classList.add('criteria-wrapper');
            
            // Add logical operator radio buttons if not first criteria
            if (builder.children.length > 0) {
                const logicalOperatorGroup = document.createElement('div');
                logicalOperatorGroup.classList.add('logical-operator-group');
                logicalOperatorGroup.innerHTML = `
                    <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                    <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                `;
                wrapper.appendChild(logicalOperatorGroup);
            }

            const newRow = document.createElement('div');
            newRow.classList.add('criteria-row');
            newRow.innerHTML = `
                <div class="drag-handle">☰</div>
                <select name="criteria[${criteriaIndex}][type]" class="criteria-type">
                    {% for criterion in criteria_list %}
                    <option value="{{ criterion }}">{{ criterion }}</option>
                    {% endfor %}
                </select>
                <select name="criteria[${criteriaIndex}][operator]" class="criteria-operator">
                    <option value="equals">equals</option>
                    <option value="contains">contains</option>
                    <option value="starts_with">starts with</option>
                </select>
                <input type="text" name="criteria[${criteriaIndex}][value]" placeholder="Enter value">
                <div class="criteria-actions">
                    <button type="button" class="icon-button" onclick="resetCriteria(this)">↻</button>
                    <button type="button" class="icon-button" onclick="deleteCriteria(this)">🗑</button>
                    <button type="button" class="icon-button" onclick="createGroup(this)">Group</button>
                </div>
            `;
            wrapper.appendChild(newRow);
            builder.appendChild(wrapper);

            criteriaIndex++;
            initializeSortable(newRow.closest('.criteria-container'));
        }

        function createGroup(button) {
            const wrapper = button.closest('.criteria-wrapper');
            const container = wrapper.parentElement;
            
            // Get the logical operator if it exists
            const logicalOperator = wrapper.querySelector('.logical-operator-group');
            let logicalOperatorHTML = '';
            if (logicalOperator) {
                const radioInputs = logicalOperator.querySelectorAll('input[type="radio"]');
                const checkedValue = Array.from(radioInputs).find(input => input.checked)?.value || 'AND';
                logicalOperatorHTML = `
                    <div class="header-logical-operator">
                        <label><input type="radio" name="${radioInputs[0].name}" value="AND" ${checkedValue === 'AND' ? 'checked' : ''}> AND</label>
                        <label><input type="radio" name="${radioInputs[0].name}" value="OR" ${checkedValue === 'OR' ? 'checked' : ''}> OR</label>
                    </div>
                `;
                // Remove the original logical operator
                logicalOperator.remove();
            }
            
            // Create new group container
            const groupContainer = document.createElement('div');
            groupContainer.classList.add('criteria-group');
            groupContainer.innerHTML = `
                <div class="group-header">
                    ${logicalOperatorHTML}
                    <button type="button" class="icon-button" onclick="disbandGroup(this)">Disband</button>
                </div>
                <div class="criteria-container">
                    <input type="hidden" name="criteria[${criteriaIndex}][isGroup]" value="true">
                </div>
            `;
            
            // Move the clicked wrapper into the new group
            const criteriaContainer = groupContainer.querySelector('.criteria-container');
            criteriaContainer.appendChild(wrapper);
            
            // Insert the group where the original wrapper was
            container.appendChild(groupContainer);
            
            // Initialize sortable for the new group
            initializeSortable(criteriaContainer);
        }

        function disbandGroup(button) {
            const group = button.closest('.criteria-group');
            const parentContainer = group.parentElement;
            const criteriaContainer = group.querySelector('.criteria-container');
            const groupElements = Array.from(criteriaContainer.children);
            
            // Get the position where the group currently is
            const groupIndex = Array.from(parentContainer.children).indexOf(group);
            
            // Process and move each element
            groupElements.forEach((element, index) => {
                if (element.classList.contains('criteria-wrapper')) {
                    // If this isn't the first element in the group and it doesn't have a logical operator,
                    // we need to add one
                    if (index > 0 && !element.querySelector('.logical-operator-group')) {
                        const logicalOperatorGroup = document.createElement('div');
                        logicalOperatorGroup.classList.add('logical-operator-group');
                        logicalOperatorGroup.innerHTML = `
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                        `;
                        element.insertBefore(logicalOperatorGroup, element.firstChild);
                    }
                    // Insert at the group's position
                    parentContainer.insertBefore(element, group);
                } else if (element.classList.contains('criteria-row')) {
                    // Create a wrapper for any unwrapped criteria rows
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('criteria-wrapper');
                    
                    // Add logical operator if needed
                    if (index > 0) {
                        const logicalOperatorGroup = document.createElement('div');
                        logicalOperatorGroup.classList.add('logical-operator-group');
                        logicalOperatorGroup.innerHTML = `
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                        `;
                        wrapper.appendChild(logicalOperatorGroup);
                    }
                    
                    wrapper.appendChild(element);
                    parentContainer.insertBefore(wrapper, group);
                }
            });
            
            // Remove the empty group
            group.remove();
            
            // Reinitialize sortable for the parent container
            initializeSortable(parentContainer);
            
            // Update form names
            updateFormNames(document.getElementById('criteriaBuilder'));
        }

        function resetCriteria(button) {
            const row = button.closest('.criteria-row');
            row.querySelector('select[name^="criteria"]').selectedIndex = 0;
            row.querySelector('select[name$="[operator]"]').selectedIndex = 0;
            row.querySelector('input[type="text"]').value = '';
        }

        function deleteCriteria(button) {
            const wrapper = button.closest('.criteria-wrapper');
            wrapper.remove();
            updateFormNames(document.getElementById('criteriaBuilder'));
        }

        function initializeSortable(container) {
            if (!container) return;
            
            Sortable.create(container, {
                animation: 150,
                handle: '.drag-handle',
                draggable: '.criteria-wrapper, .criteria-group',
                group: 'criteria',
                onEnd: function(evt) {
                    updateFormNames(document.getElementById('criteriaBuilder'));
                }
            });
        }

        function updateFormNames(container, prefix = '') {
            let index = 0;
            container.querySelectorAll(':scope > .criteria-wrapper, :scope > .criteria-group').forEach((el, idx) => {
                if (el.classList.contains('criteria-wrapper')) {
                    // Update logical operator name if not first item
                    if (idx > 0) {
                        const logicalOp = el.querySelector('.logical-operator-group input[type="radio"]');
                        if (logicalOp) {
                            const baseName = `${prefix}criteria[logical][${index - 1}]`;
                            el.querySelectorAll('.logical-operator-group input[type="radio"]').forEach(radio => {
                                radio.name = baseName;
                            });
                        }
                    }
                    
                    // Update criteria row names
                    const row = el.querySelector('.criteria-row');
                    if (row) {
                        updateRowNames(row, prefix, index);
                        index++;
                    }
                } else if (el.classList.contains('criteria-group')) {
                    const groupPrefix = `${prefix}criteria[${index}].`;
                    el.querySelector('input[name$="[isGroup]"]').name = `${prefix}criteria[${index}][isGroup]`;
                    updateFormNames(el.querySelector('.criteria-container'), groupPrefix);
                    index++;
                }
            });
        }

        function updateRowNames(row, prefix, index) {
            row.querySelector('select[name$="[type]"]').name = `${prefix}criteria[${index}][type]`;
            row.querySelector('select[name$="[operator]"]').name = `${prefix}criteria[${index}][operator]`;
            row.querySelector('input[type="text"]').name = `${prefix}criteria[${index}][value]`;
        }

        document.addEventListener('DOMContentLoaded', function() {
            initializeSortable(document.getElementById('criteriaBuilder'));
        });
    </script>
    <style>
        .criteria-wrapper {
            margin: 5px 0;
        }
        .drag-handle {
            cursor: grab;
            display: inline-block;
            margin-right: 10px;
        }
        .criteria-group {
            border: 2px solid #4a90e2;
            border-radius: 4px;
            margin: 10px 0;
            padding: 10px;
        }
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #4a90e2;
        }
        .header-logical-operator {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .header-logical-operator label {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .criteria-container {
            min-height: 50px;
            padding: 5px;
        }
        .logical-operator-group {
            margin: 5px 0;
            padding-left: 25px;
        }
    </style>
</head>
<body>
    <!-- Previous sidebar HTML remains unchanged -->
    <div class="sidebar">
        <h2>Computers</h2>
        <a href="#">Inventory</a>
        <a href="#">Search Inventory</a>
        <a href="#">Search Volume Content</a>
        <a href="#">Licensed Software</a>
        <h2>Groups</h2>
        <a href="/">Smart Computer Groups</a>
        <a href="#">Static Computer Groups</a>
        <a href="#">Classes</a>
    </div>
    <div class="content">
        <h1>Create New Smart Group</h1>
        <form method="POST">
            <!-- Previous form HTML remains unchanged -->
            <h2>General</h2>
            <p class="section-desc">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.</p>
            <br>
            <h3>About</h3>
            <hr>
            <br>
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" placeholder="Give this smart group a memorable name" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea id="description" name="description" rows="3" placeholder="Describe what this smart group is used for."></textarea>
            </div>
            <br>
            <h3>Organization</h3>
            <hr>
            <br>
            <div class="form-group" style="display: flex; align-items: center;">
                <label for="tags" style="margin-right: 10px; width: 150px;">Tags</label>
                <input type="text" id="tags" name="tags" placeholder="Search tags  🔍">
            </div>

            <h2>Criteria</h2>
            <hr>
            <br>
            <p class="section-desc">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.</p>
            
            <div id="criteriaBuilder" class="criteria-container">
                <div class="criteria-row">
                    <div class="drag-handle">☰</div>
                    <select name="criteria[0][type]" class="criteria-type">
                        {% for criterion in criteria_list %}
                        <option value="{{ criterion }}">{{ criterion }}</option>
                        {% endfor %}
                    </select>
                    <select name="criteria[0][operator]" class="criteria-operator">
                        <option value="equals">equals</option>
                        <option value="contains">contains</option>
                        <option value="starts_with">starts with</option>
                    </select>
                    <input type="text" name="criteria[0][value]" placeholder="Enter value">
                    <div class="criteria-actions">
                        <button type="button" class="icon-button" onclick="resetCriteria(this)">↻</button>
                        <button type="button" class="icon-button" onclick="deleteCriteria(this)">🗑</button>
                        <button type="button" class="icon-button" onclick="createGroup(this)">Group</button>
                    </div>
                </div>
            </div>

            <div class="add-criteria-container">
                <button type="button" class="add-criteria" onclick="addCriteria()">Add Criteria</button>
            </div>
            <br><br>
            <div class="form-group">
                <label><input type="checkbox" name="isEnabled"> Enable Smart Group</label>
            </div>
            <br>
            <button type="submit">Create Group</button>
        </form>
    </div>
</body>
</html>
    ''', criteria_list=criteria_list)



@app.route('/edit-smart-group/<int:index>', methods=['GET', 'POST'])
def edit_smart_computer_group(index):
    group = smart_groups[index]

    if request.method == 'POST':
        group['name'] = request.form['name']
        group['description'] = request.form['description']
        group['isEnabled'] = 'isEnabled' in request.form

        def parse_criteria_group(form_data, prefix=''):
            criteria = []
            index = 0
            while f'{prefix}criteria[{index}][type]' in form_data or f'{prefix}criteria[{index}][isGroup]' in form_data:
                crit_data = {}
                
                if f'{prefix}criteria[{index}][isGroup]' in form_data:
                    crit_data = {
                        "isGroup": True,
                        "criteria": parse_criteria_group(form_data, f'{prefix}criteria[{index}].'),
                        "logical_operator": None
                    }
                    if index > 0:
                        crit_data["logical_operator"] = form_data.get(f'{prefix}criteria[logical][{index - 1}]', 'AND')
                else:
                    crit_data = {
                        "isGroup": False,
                        "type": form_data.get(f'{prefix}criteria[{index}][type]'),
                        "operator": form_data.get(f'{prefix}criteria[{index}][operator]'),
                        "value": form_data.get(f'{prefix}criteria[{index}][value]'),
                        "logical_operator": form_data.get(f'{prefix}criteria[logical][{index - 1}]', 'AND') if index > 0 else None
                    }

                criteria.append(crit_data)
                index += 1
            return criteria

        parsed_criteria = parse_criteria_group(request.form)
        root_group = {
            "isGroup": True,
            "criteria": parsed_criteria,
            "logical_operator": None
        }
        group['criteria'] = [root_group]
        return redirect(url_for('smart_computer_groups_dashboard'))

    def format_criteria_for_template(criteria, prefix=''):
        formatted = []
        for idx, crit in enumerate(criteria):
            current_index = f"{prefix}{idx}" if prefix else str(idx)
            
            if crit.get('isGroup', False):
                next_prefix = f"{current_index}."
                nested_criteria = format_criteria_for_template(crit['criteria'], next_prefix)
                formatted.append({
                    'isGroup': True,
                    'index': current_index,
                    'logical_operator': crit.get('logical_operator'),
                    'criteria': nested_criteria
                })
            else:
                formatted.append({
                    'isGroup': False,
                    'index': current_index,
                    'type': crit.get('type', ''),
                    'operator': crit.get('operator', ''),
                    'value': crit.get('value', ''),
                    'logical_operator': crit.get('logical_operator')
                })
        return formatted

    root_criteria = group.get('criteria', [])
    if root_criteria and isinstance(root_criteria[0], dict) and root_criteria[0].get('isGroup'):
        parsed_criteria = format_criteria_for_template(root_criteria[0]['criteria'])
    else:
        parsed_criteria = []
        if root_criteria:
            root_group = {
                "isGroup": True,
                "criteria": root_criteria,
                "logical_operator": None
            }
            group['criteria'] = [root_group]
            parsed_criteria = format_criteria_for_template(root_criteria)

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Smart Computer Group</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.15.0/Sortable.min.js"></script>
    <script>
        let criteriaIndex = {{ parsed_criteria|length }};

        function addCriteria(container = null) {
            const builder = container || document.getElementById('criteriaBuilder');
            const wrapper = document.createElement('div');
            wrapper.classList.add('criteria-wrapper');
            
            if (builder.children.length > 0) {
                const logicalOperatorGroup = document.createElement('div');
                logicalOperatorGroup.classList.add('logical-operator-group');
                logicalOperatorGroup.innerHTML = `
                    <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                    <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                `;
                wrapper.appendChild(logicalOperatorGroup);
            }

            const newRow = document.createElement('div');
            newRow.classList.add('criteria-row');
            newRow.innerHTML = `
                <div class="drag-handle">☰</div>
                <select name="criteria[${criteriaIndex}][type]" class="criteria-type">
                    {% for criterion in criteria_list %}
                    <option value="{{ criterion }}">{{ criterion }}</option>
                    {% endfor %}
                </select>
                <select name="criteria[${criteriaIndex}][operator]" class="criteria-operator">
                    <option value="equals">equals</option>
                    <option value="contains">contains</option>
                    <option value="starts_with">starts with</option>
                </select>
                <input type="text" name="criteria[${criteriaIndex}][value]" placeholder="Enter value">
                <div class="criteria-actions">
                    <button type="button" class="icon-button" onclick="resetCriteria(this)">↻</button>
                    <button type="button" class="icon-button" onclick="deleteCriteria(this)">🗑</button>
                    <button type="button" class="icon-button" onclick="createGroup(this)">Group</button>
                </div>
            `;
            wrapper.appendChild(newRow);
            builder.appendChild(wrapper);

            criteriaIndex++;
            initializeSortable(newRow.closest('.criteria-container'));
        }

        function createGroup(button) {
            const wrapper = button.closest('.criteria-wrapper');
            const container = wrapper.parentElement;
            
            const logicalOperator = wrapper.querySelector('.logical-operator-group');
            let logicalOperatorHTML = '';
            if (logicalOperator) {
                const radioInputs = logicalOperator.querySelectorAll('input[type="radio"]');
                const checkedValue = Array.from(radioInputs).find(input => input.checked)?.value || 'AND';
                logicalOperatorHTML = `
                    <div class="header-logical-operator">
                        <label><input type="radio" name="${radioInputs[0].name}" value="AND" ${checkedValue === 'AND' ? 'checked' : ''}> AND</label>
                        <label><input type="radio" name="${radioInputs[0].name}" value="OR" ${checkedValue === 'OR' ? 'checked' : ''}> OR</label>
                    </div>
                `;
                logicalOperator.remove();
            }
            
            const groupContainer = document.createElement('div');
            groupContainer.classList.add('criteria-group');
            groupContainer.innerHTML = `
                <div class="group-header">
                    ${logicalOperatorHTML}
                    <button type="button" class="icon-button" onclick="disbandGroup(this)">Disband</button>
                </div>
                <div class="criteria-container">
                    <input type="hidden" name="criteria[${criteriaIndex}][isGroup]" value="true">
                </div>
            `;
            
            const criteriaContainer = groupContainer.querySelector('.criteria-container');
            criteriaContainer.appendChild(wrapper);
            container.appendChild(groupContainer);
            initializeSortable(criteriaContainer);
        }

        function disbandGroup(button) {
            const group = button.closest('.criteria-group');
            const parentContainer = group.parentElement;
            const criteriaContainer = group.querySelector('.criteria-container');
            const groupElements = Array.from(criteriaContainer.children);
            
            groupElements.forEach((element, index) => {
                if (element.classList.contains('criteria-wrapper')) {
                    if (index > 0 && !element.querySelector('.logical-operator-group')) {
                        const logicalOperatorGroup = document.createElement('div');
                        logicalOperatorGroup.classList.add('logical-operator-group');
                        logicalOperatorGroup.innerHTML = `
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                        `;
                        element.insertBefore(logicalOperatorGroup, element.firstChild);
                    }
                    parentContainer.insertBefore(element, group);
                } else if (element.classList.contains('criteria-row')) {
                    const wrapper = document.createElement('div');
                    wrapper.classList.add('criteria-wrapper');
                    
                    if (index > 0) {
                        const logicalOperatorGroup = document.createElement('div');
                        logicalOperatorGroup.classList.add('logical-operator-group');
                        logicalOperatorGroup.innerHTML = `
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="AND" checked> AND</label>
                            <label><input type="radio" name="criteria[logical][${criteriaIndex - 1}]" value="OR"> OR</label>
                        `;
                        wrapper.appendChild(logicalOperatorGroup);
                    }
                    
                    wrapper.appendChild(element);
                    parentContainer.insertBefore(wrapper, group);
                }
            });
            
            group.remove();
            initializeSortable(parentContainer);
            updateFormNames(document.getElementById('criteriaBuilder'));
        }

        function resetCriteria(button) {
            const row = button.closest('.criteria-row');
            row.querySelector('select[name^="criteria"]').selectedIndex = 0;
            row.querySelector('select[name$="[operator]"]').selectedIndex = 0;
            row.querySelector('input[type="text"]').value = '';
        }

        function deleteCriteria(button) {
            const wrapper = button.closest('.criteria-wrapper');
            wrapper.remove();
            updateFormNames(document.getElementById('criteriaBuilder'));
        }

        function initializeSortable(container) {
            if (!container) return;
            
            Sortable.create(container, {
                animation: 150,
                handle: '.drag-handle',
                draggable: '.criteria-wrapper, .criteria-group',
                group: 'criteria',
                onEnd: function(evt) {
                    updateFormNames(document.getElementById('criteriaBuilder'));
                }
            });
        }

        function updateFormNames(container, prefix = '') {
            let index = 0;
            container.querySelectorAll(':scope > .criteria-wrapper, :scope > .criteria-group').forEach((el, idx) => {
                if (el.classList.contains('criteria-wrapper')) {
                    if (idx > 0) {
                        const logicalOp = el.querySelector('.logical-operator-group input[type="radio"]');
                        if (logicalOp) {
                            const baseName = `${prefix}criteria[logical][${index - 1}]`;
                            el.querySelectorAll('.logical-operator-group input[type="radio"]').forEach(radio => {
                                radio.name = baseName;
                            });
                        }
                    }
                    
                    const row = el.querySelector('.criteria-row');
                    if (row) {
                        updateRowNames(row, prefix, index);
                        index++;
                    }
                } else if (el.classList.contains('criteria-group')) {
                    const groupPrefix = `${prefix}criteria[${index}].`;
                    el.querySelector('input[name$="[isGroup]"]').name = `${prefix}criteria[${index}][isGroup]`;
                    updateFormNames(el.querySelector('.criteria-container'), groupPrefix);
                    index++;
                }
            });
        }

        function updateRowNames(row, prefix, index) {
            row.querySelector('select[name$="[type]"]').name = `${prefix}criteria[${index}][type]`;
            row.querySelector('select[name$="[operator]"]').name = `${prefix}criteria[${index}][operator]`;
            row.querySelector('input[type="text"]').name = `${prefix}criteria[${index}][value]`;
        }

        document.addEventListener('DOMContentLoaded', function() {
            initializeSortable(document.getElementById('criteriaBuilder'));
        });
    </script>
    <style>
        .criteria-wrapper {
            margin: 5px 0;
        }
        .drag-handle {
            cursor: grab;
            display: inline-block;
            margin-right: 10px;
        }
        .criteria-group {
            border: 2px solid #4a90e2;
            border-radius: 4px;
            margin: 10px 0;
            padding: 10px;
        }
        .root-group {
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .root-group > .group-header {
            display: none !important;
        }
        .group-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #4a90e2;
        }
        .criteria-container {
            min-height: 50px;
            padding: 5px;
        }
        .logical-operator-group {
            margin: 5px 0;
            padding-left: 25px;
        }
        .header-logical-operator {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .header-logical-operator label {
            display: flex;
            align-items: center;
            gap: 4px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Computers</h2>
        <a href="#">Inventory</a>
        <a href="#">Search Inventory</a>
        <a href="#">Search Volume Content</a>
        <a href="#">Licensed Software</a>
        <h2>Groups</h2>
        <a href="/">Smart Computer Groups</a>
        <a href="#">Static Computer Groups</a>
        <a href="#">Classes</a>
    </div>
    <div class="content">
        <h1>Edit Smart Group: {{ group['name'] }}</h1>
        <form method="POST">
            <h2>General</h2>
            <p class="section-desc">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.</p>
            <br>
            <h3>About</h3>
            <hr>
            <br>
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" name="name" value="{{ group['name'] }}" required>
            </div>
            <div class="form-group">
                <label for="description">Description</label>
                <textarea name="description">{{ group['description'] }}</textarea>
            </div>
            <br>
            <h3>Organization</h3>
            <hr>
            <br>
            <div class="form-group" style="display: flex; align-items: center;">
                <label for="tags" style="margin-right: 10px; width: 150px;">Tags</label>
                <input type="text" id="tags" name="tags" placeholder="Search tags  🔍">
            </div>

            <h2>Criteria</h2>
            <hr>
            <br>
            <p class="section-desc">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.</p>
            
            <div id="criteriaBuilder" class="criteria-container">
                <div class="criteria-group root-group">
                    <div class="criteria-container">
                        {% macro render_criteria(criteria_list, prefix='') %}
                            {% for crit in criteria_list %}
                                {% if crit.isGroup %}
                                    <div class="criteria-group">
                                        <div class="group-header">
                                            {% if not loop.first %}
                                                <div class="header-logical-operator">
                                                    <label><input type="radio" name="criteria[logical][{{ crit.index }}]" value="AND" {% if crit.logical_operator == 'AND' %}checked{% endif %}> AND</label>
                                                    <label><input type="radio" name="criteria[logical][{{ crit.index }}]" value="OR" {% if crit.logical_operator == 'OR' %}checked{% endif %}> OR</label>
                                                </div>
                                            {% endif %}
                                            <button type="button" class="icon-button" onclick="disbandGroup(this)">Disband</button>
                                        </div>
                                        <div class="criteria-container">
                                            <input type="hidden" name="criteria[{{ crit.index }}][isGroup]" value="true">
                                            {{ render_criteria(crit.criteria) }}
                                        </div>
                                    </div>
                                {% else %}
                                    <div class="criteria-wrapper">
                                        {% if not loop.first %}
                                            <div class="logical-operator-group">
                                                <label><input type="radio" name="criteria[logical][{{ crit.index }}]" value="AND" {% if crit.logical_operator == 'AND' %}checked{% endif %}> AND</label>
                                                <label><input type="radio" name="criteria[logical][{{ crit.index }}]" value="OR" {% if crit.logical_operator == 'OR' %}checked{% endif %}> OR</label>
                                            </div>
                                        {% endif %}
                                        <div class="criteria-row">
                                            <div class="drag-handle">☰</div>
                                            <select name="criteria[{{ crit.index }}][type]">
                                                {% for criterion in criteria_list %}
                                                    <option value="{{ criterion }}" {% if criterion == crit.type %}selected{% endif %}>{{ criterion }}</option>
                                                {% endfor %}
                                            </select>
                                            <select name="criteria[{{ crit.index }}][operator]">
                                                <option value="equals" {% if crit.operator == 'equals' %}selected{% endif %}>equals</option>
                                                <option value="contains" {% if crit.operator == 'contains' %}selected{% endif %}>contains</option>
                                                <option value="starts_with" {% if crit.operator == 'starts_with' %}selected{% endif %}>starts with</option>
                                            </select>
                                            <input type="text" name="criteria[{{ crit.index }}][value]" value="{{ crit.value }}">
                                            <div class="criteria-actions">
                                                <button type="button" class="icon-button" onclick="resetCriteria(this)">↻</button>
                                                <button type="button" class="icon-button" onclick="deleteCriteria(this)">🗑</button>
                                                <button type="button" class="icon-button" onclick="createGroup(this)">Group</button>
                                            </div>
                                        </div>
                                    </div>
                                {% endif %}
                            {% endfor %}
                        {% endmacro %}

                        {{ render_criteria(parsed_criteria) }}
                    </div>
                </div>
            </div>

            <div class="add-criteria-container">
                <button type="button" class="add-criteria" onclick="addCriteria()">Add Criteria</button>
            </div>
            <br><br>
            <div class="form-group">
                <label><input type="checkbox" name="isEnabled" {% if group['isEnabled'] %}checked{% endif %}> Enable Smart Group</label>
            </div>
            <br>
            <button type="submit">Save</button>
        </form>
    </div>
</body>
</html>
    ''',group=group, parsed_criteria=parsed_criteria, criteria_list=['App Name', 'AppleCare ID', 'App Analytics Enabled', 'AirPlay Password', 'OS Version'])


if __name__ == '__main__':
    app.run(debug=True)
