// Main JavaScript file for Gestion Immobilière

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Property gallery image switcher
    const mainImage = document.querySelector('.property-gallery .main-image');
    const thumbnails = document.querySelectorAll('.property-gallery .thumbnail');
    
    if (mainImage && thumbnails.length > 0) {
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', function() {
                // Update main image
                mainImage.src = this.src;
                
                // Update active state
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // AJAX form submission with loading spinner
    const ajaxForms = document.querySelectorAll('.ajax-form');
    
    Array.from(ajaxForms).forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Show loading spinner
            showSpinner();
            
            // Get form data
            const formData = new FormData(form);
            
            // Send AJAX request
            fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Hide spinner
                hideSpinner();
                
                // Handle response
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message);
                    
                    // Redirect if needed
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                } else {
                    // Show error message
                    showAlert('danger', data.message || 'Une erreur est survenue.');
                }
            })
            .catch(error => {
                // Hide spinner
                hideSpinner();
                
                // Show error message
                showAlert('danger', 'Une erreur est survenue lors de la communication avec le serveur.');
                console.error('Error:', error);
            });
        });
    });

    // Dynamic form fields
    setupDynamicFormFields();

    // Filter form handling
    setupFilterForms();

    // Data tables initialization
    initializeDataTables();
});

// Show loading spinner
function showSpinner() {
    // Create spinner if it doesn't exist
    if (!document.querySelector('.spinner-overlay')) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Chargement...</span></div>';
        document.body.appendChild(spinner);
    } else {
        document.querySelector('.spinner-overlay').style.display = 'flex';
    }
}

// Hide loading spinner
function hideSpinner() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

// Show alert message
function showAlert(type, message) {
    // Create alert container if it doesn't exist
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '9999';
        document.body.appendChild(alertContainer);
    }
    
    // Create alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add alert to container
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alert.remove();
        }, 150);
    }, 5000);
}

// Setup dynamic form fields
function setupDynamicFormFields() {
    // Add amenity field
    const addAmenityBtn = document.getElementById('add-amenity-btn');
    if (addAmenityBtn) {
        addAmenityBtn.addEventListener('click', function() {
            const amenitiesContainer = document.getElementById('amenities-container');
            const amenityIndex = amenitiesContainer.children.length;
            
            const amenityRow = document.createElement('div');
            amenityRow.className = 'row mb-3 amenity-row';
            amenityRow.innerHTML = `
                <div class="col-md-5">
                    <select name="amenities[${amenityIndex}][id]" class="form-select" required>
                        <option value="">Sélectionner un équipement</option>
                        <!-- Options will be populated by AJAX -->
                    </select>
                </div>
                <div class="col-md-5">
                    <input type="text" name="amenities[${amenityIndex}][notes]" class="form-control" placeholder="Notes (optionnel)">
                </div>
                <div class="col-md-2">
                    <button type="button" class="btn btn-danger remove-amenity-btn">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            amenitiesContainer.appendChild(amenityRow);
            
            // Load amenities via AJAX
            loadAmenities(amenityRow.querySelector('select'));
            
            // Add remove event listener
            amenityRow.querySelector('.remove-amenity-btn').addEventListener('click', function() {
                amenityRow.remove();
            });
        });
    }
}

// Load amenities via AJAX
function loadAmenities(selectElement) {
    fetch('/api/properties/amenities')
        .then(response => response.json())
        .then(data => {
            if (data.amenities && data.amenities.length > 0) {
                // Group amenities by category
                const categories = {};
                data.amenities.forEach(amenity => {
                    if (!categories[amenity.category]) {
                        categories[amenity.category] = [];
                    }
                    categories[amenity.category].push(amenity);
                });
                
                // Add options to select
                for (const category in categories) {
                    const optgroup = document.createElement('optgroup');
                    optgroup.label = category.charAt(0).toUpperCase() + category.slice(1);
                    
                    categories[category].forEach(amenity => {
                        const option = document.createElement('option');
                        option.value = amenity.id;
                        option.textContent = amenity.name;
                        optgroup.appendChild(option);
                    });
                    
                    selectElement.appendChild(optgroup);
                }
            }
        })
        .catch(error => {
            console.error('Error loading amenities:', error);
        });
}

// Setup filter forms
function setupFilterForms() {
    const filterForms = document.querySelectorAll('.filter-form');
    
    Array.from(filterForms).forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Get form data
            const formData = new FormData(form);
            
            // Convert to URL parameters
            const params = new URLSearchParams();
            for (const [key, value] of formData.entries()) {
                if (value) {
                    params.append(key, value);
                }
            }
            
            // Redirect to current page with filters
            window.location.href = `${window.location.pathname}?${params.toString()}`;
        });
        
        // Reset button
        const resetBtn = form.querySelector('.reset-filters-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                window.location.href = window.location.pathname;
            });
        }
    });
}

// Initialize data tables
function initializeDataTables() {
    const dataTables = document.querySelectorAll('.data-table');
    
    if (dataTables.length > 0 && typeof $.fn.DataTable !== 'undefined') {
        Array.from(dataTables).forEach(table => {
            $(table).DataTable({
                language: {
                    url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/French.json'
                },
                responsive: true
            });
        });
    }
}
