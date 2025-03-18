// Global autosave functionality
let autoSaveTimer;
const AUTO_SAVE_DELAY = 3000; // 3 seconds

// Initialize tooltips and popovers
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
    $('[data-toggle="popover"]').popover();
});

// Handle todo item completion toggle - Updated for dashboard only
function toggleTodoComplete(todoId) {
    $.ajax({
        url: `/todo/${todoId}/toggle`,
        type: 'POST',
        success: function(response) {
            if (response.status === 'success') {
                const todoItem = $(`#todo-${todoId}`);
                if (response.completed) {
                    todoItem.addClass('completed');
                    todoItem.find('.todo-checkbox').prop('checked', true);
                    todoItem.find('label.form-check-label').addClass('text-muted');
                    todoItem.data('completed', true);
                } else {
                    todoItem.removeClass('completed');
                    todoItem.find('.todo-checkbox').prop('checked', false);
                    todoItem.find('label.form-check-label').removeClass('text-muted');
                    todoItem.data('completed', false);
                }
                
                // Update the completed count in the badge
                updateTodoCountBadge();
            }
        },
        error: function(error) {
            console.error('Error toggling todo item:', error);
            alert('Failed to update task status. Please try again.');
        }
    });
}

// Function to update todo count badge
function updateTodoCountBadge() {
    const totalTodos = $('#dashboard-todo-list li').length;
    const completedTodos = $('#dashboard-todo-list li.completed').length;
    const $badge = $('.card-header .badge.bg-success');
    
    if ($badge.length) {
        $badge.text(`${completedTodos}/${totalTodos} Completed`);
    }
}

// Handle team member task completion toggle
function toggleMemberTaskComplete(taskId) {
    $.ajax({
        url: `/team/task/${taskId}/toggle`,
        type: 'POST',
        success: function(response) {
            if (response.status === 'success') {
                const taskItem = $(`#task-${taskId}`);
                if (response.completed) {
                    taskItem.addClass('completed');
                    taskItem.find('.task-checkbox').prop('checked', true);
                    taskItem.find('label.form-check-label').addClass('text-muted');
                } else {
                    taskItem.removeClass('completed');
                    taskItem.find('.task-checkbox').prop('checked', false);
                    taskItem.find('label.form-check-label').removeClass('text-muted');
                }
            }
        },
        error: function(error) {
            console.error('Error toggling task item:', error);
            alert('Failed to update task status. Please try again.');
        }
    });
}

// Generic autosave function for forms
function setupAutosave(formSelector, saveUrl, getDataFunction) {
    const form = $(formSelector);
    if (!form.length) return;
    
    // Set up change event listeners on all form inputs
    form.find('input, textarea, select').on('input change', function() {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(() => {
            const formData = getDataFunction();
            
            $.ajax({
                url: saveUrl,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(formData),
                success: function(response) {
                    // Show a subtle "Saved" message that fades out
                    const savedMsg = $('<div class="autosave-notification">Saved</div>');
                    savedMsg.css({
                        'position': 'fixed',
                        'bottom': '20px',
                        'right': '20px',
                        'background-color': 'rgba(40, 167, 69, 0.9)',
                        'color': 'white',
                        'padding': '10px 20px',
                        'border-radius': '5px',
                        'z-index': '9999'
                    });
                    
                    $('body').append(savedMsg);
                    setTimeout(() => {
                        savedMsg.fadeOut(300, function() { $(this).remove(); });
                    }, 2000);
                },
                error: function(error) {
                    console.error('Error autosaving:', error);
                }
            });
        }, AUTO_SAVE_DELAY);
    });
}

// Setup color picker in settings
function setupColorPicker() {
    const colorSwatches = $('.color-swatch');
    const colorInput = $('#accent_color');
    
    if (!colorSwatches.length) return;
    
    // Set initial selected swatch
    const currentColor = colorInput.val();
    colorSwatches.each(function() {
        if ($(this).data('color') === currentColor) {
            $(this).addClass('selected');
        }
    });
    
    // Handle swatch click
    colorSwatches.on('click', function() {
        const color = $(this).data('color');
        colorInput.val(color);
        colorSwatches.removeClass('selected');
        $(this).addClass('selected');
    });
}

// Document ready handler
$(document).ready(function() {
    // Initialize color picker if on settings page
    setupColorPicker();
    
    // Handle embedded link clicks to open in new tab/window
    $('.external-link').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        window.open(url, '_blank');
    });
});