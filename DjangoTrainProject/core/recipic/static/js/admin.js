// Function to add a new instruction step
function addStep() {
    const container = document.getElementById('instructions-container');
    const stepDiv = document.createElement('div');
    stepDiv.className = 'instruction-step';
    
    stepDiv.innerHTML = `
        <textarea name="steps[]" required></textarea>
        <button type="button" class="btn btn-remove" onclick="removeStep(this)">Remove</button>
    `;
    
    container.appendChild(stepDiv);
}

// Function to remove an instruction step
function removeStep(button) {
    const container = document.getElementById('instructions-container');
    const stepDiv = button.parentElement;
    
    // Don't remove if it's the last step
    if (container.children.length > 1) {
        container.removeChild(stepDiv);
    }
}

// Confirm delete
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this recipe?')) {
                e.preventDefault();
            }
        });
    });
});


function addStep() {
    // Get the container where steps are stored
    const container = document.getElementById('instructions-container');
    
    // Create new step div
    const stepDiv = document.createElement('div');
    stepDiv.className = 'instruction-step';
    
    // Create textarea
    const textarea = document.createElement('textarea');
    textarea.name = 'steps[]';
    textarea.required = true;
    
    // Create remove button
    const removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'btn btn-remove';
    removeButton.onclick = function() { removeStep(this); };
    removeButton.textContent = 'Remove';
    
    // Add elements to step div
    stepDiv.appendChild(textarea);
    stepDiv.appendChild(removeButton);
    
    // Add the new step to container
    container.appendChild(stepDiv);
}

function removeStep(button) {
    const stepDiv = button.parentElement;
    // Only remove if there's more than one step
    if (document.getElementsByClassName('instruction-step').length > 1) {
        stepDiv.remove();
    }
}

