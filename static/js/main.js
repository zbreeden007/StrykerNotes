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

// Function to refresh the todo list via AJAX
function refreshTodoList() {
    $.ajax({
        url: '/get_todos',
        type: 'GET',
        success: function(response) {
            // Replace the todo list HTML with the updated version
            $('#dashboard-todo-list').html(response);
            
            // Re-initialize sortable if needed
            initTodoSortable();
        },
        error: function(error) {
            console.error('Error refreshing todo list:', error);
        }
    });
}

// Initialize the todo list sorting functionality
function initTodoSortable() {
    const todoList = document.getElementById('dashboard-todo-list');
    if (todoList) {
        // Check if there's an existing Sortable instance and destroy it
        if (todoList.sortable) {
            todoList.sortable.destroy();
        }
        
        // Create a new Sortable instance
        const sortableInstance = new Sortable(todoList, {
            animation: 150,
            // Remove the handle selector to make the entire item draggable
            // handle: '.handle',
            ghostClass: 'sortable-ghost',
            // Add a different dragging class for visual feedback
            chosenClass: 'sortable-chosen',
            dragClass: 'sortable-drag',
            onEnd: function(evt) {
                const todoIds = Array.from(todoList.children)
                    .map(item => item.id.replace('todo-', ''));
                
                // Show visual feedback that saving is in progress
                todoList.classList.add('saving-in-progress');
                
                // Send the new order to the server
                fetch('/todo/reorder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ todoIds: todoIds })
                })
                .then(response => response.json())
                .then(data => {
                    todoList.classList.remove('saving-in-progress');
                    
                    if (data.status === 'success') {
                        // Add visual feedback of success
                        todoList.style.backgroundColor = '#d4edda';
                        setTimeout(() => {
                            todoList.style.backgroundColor = '';
                        }, 500);
                    } else {
                        console.error('Error reordering todos:', data.message);
                        // Add visual feedback of error
                        todoList.style.backgroundColor = '#f8d7da';
                        setTimeout(() => {
                            todoList.style.backgroundColor = '';
                        }, 500);
                    }
                })
                .catch(error => {
                    console.error('Error reordering todos:', error);
                    todoList.classList.remove('saving-in-progress');
                    
                    // Add visual feedback of error
                    todoList.style.backgroundColor = '#f8d7da';
                    setTimeout(() => {
                        todoList.style.backgroundColor = '';
                    }, 500);
                });
            }
        });
        
        // Store the Sortable instance on the element itself
        todoList.sortable = sortableInstance;
    }
}

// Initialize the priorities container sorting functionality
function initPrioritiesSortable() {
    const prioritiesContainer = document.getElementById('priorities-container');
    if (prioritiesContainer) {
        // Check if there's an existing Sortable instance and destroy it
        if (prioritiesContainer.sortable) {
            prioritiesContainer.sortable.destroy();
        }
        
        // Create a new Sortable instance
        const sortableInstance = new Sortable(prioritiesContainer, {
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const priorityIds = Array.from(prioritiesContainer.children)
                    .filter(item => item.id && item.id.startsWith('priority-'))
                    .map(item => item.id.replace('priority-', ''));
                
                // Send the new order to the server
                fetch('/priority/reorder', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ priorityIds: priorityIds })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status !== 'success') {
                        console.error('Error reordering priorities:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error reordering priorities:', error);
                });
            }
        });
        
        // Store the Sortable instance on the element itself
        prioritiesContainer.sortable = sortableInstance;
    }
}

// Update this function to account for member-specific lists
function setupDragAndDrop(itemType, memberId) {
    const containerId = memberId ? `${itemType}-list-${memberId}` : `${itemType}-list`;
    const container = document.getElementById(containerId);
    
    if (!container) {
        console.log(`Container not found for ${containerId}`);
        return;
    }
    
    console.log(`Setting up drag and drop for ${containerId}`);
    
    // Check if there's an existing Sortable instance and destroy it
    if (container.sortable) {
        container.sortable.destroy();
    }
    
    // Create a new Sortable instance
    const sortableInstance = new Sortable(container, {
        animation: 150,
        onEnd: function (evt) {
            const itemOrder = Array.from(container.children)
                .filter(item => item.dataset && item.dataset.itemId)
                .map(item => item.dataset.itemId);
            
            if (itemOrder.length === 0) {
                console.log(`No valid items found in ${containerId}`);
                return;
            }
            
            console.log(`New order for ${itemType} items:`, itemOrder);
            
            // Show visual feedback that saving is in progress
            container.classList.add('saving-in-progress');
            
            fetch(`/team/reorder_items/${itemType}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ order: itemOrder })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(`${itemType} items reordered successfully`);
                container.classList.remove('saving-in-progress');
                
                // Add visual feedback of success
                container.style.backgroundColor = '#d4edda';
                setTimeout(() => {
                    container.style.backgroundColor = '';
                }, 500);
            })
            .catch(error => {
                console.error(`Error reordering ${itemType} items:`, error);
                container.classList.remove('saving-in-progress');
                
                // Add visual feedback of error
                container.style.backgroundColor = '#f8d7da';
                setTimeout(() => {
                    container.style.backgroundColor = '';
                }, 500);
            });
        }
    });
    
    // Store the Sortable instance on the element itself
    container.sortable = sortableInstance;
}

function enableInlineEditing(itemType) {
    console.log(`Setting up inline editing for ${itemType} items`);
    const editButtons = document.querySelectorAll(`.${itemType}-edit`);
    
    if (!editButtons.length) {
        console.log(`No edit buttons found for ${itemType} items`);
        return;
    }
    
    console.log(`Found ${editButtons.length} ${itemType} edit buttons`);
    
    editButtons.forEach(btn => {
        // Remove any existing click event listeners
        btn.removeEventListener('click', btn._clickHandler);
        
        // Create a new click handler
        btn._clickHandler = function() {
            const itemId = this.dataset.itemId;
            console.log(`Edit button clicked for ${itemType} with ID: ${itemId}`);
            
            const contentField = document.getElementById(`${itemType}-content-${itemId}`);
            if (!contentField) {
                console.error(`Content field not found for ${itemType}-content-${itemId}`);
                return;
            }
            
            // Make sure we're not already editing
            if (contentField.getAttribute('contenteditable') === 'true') {
                console.log(`Already editing ${itemType} ${itemId}`);
                return;
            }
            
            console.log(`Content field found: ${contentField.innerText}`);

            // Make the field editable
            contentField.contentEditable = 'true';
            contentField.focus();
            
            // Store original content in case we need to revert
            const originalContent = contentField.innerText;
            console.log(`Original content: ${originalContent}`);
            
            // Select all text to make it easier to replace
            const selection = window.getSelection();
            const range = document.createRange();
            range.selectNodeContents(contentField);
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Function to save the content
            const saveContent = function() {
                const updatedContent = contentField.innerText.trim();
                console.log(`Updated content: ${updatedContent}`);
                
                // Make sure we're not saving empty content
                if (updatedContent === '') {
                    contentField.innerText = originalContent;
                    contentField.contentEditable = 'false';
                    return;
                }
                
                if (updatedContent === originalContent) {
                    // No changes, don't make an API call
                    console.log('No changes detected, not saving');
                    contentField.contentEditable = 'false';
                    return;
                }
                
                // Prepare the data to send based on item type
                let data = {};
                if (itemType === 'project') {
                    data = { name: updatedContent };
                } else if (itemType === 'task') {
                    data = { content: updatedContent };
                } else if (itemType === 'development') {
                    data = { title: updatedContent };
                }
                
                console.log(`Sending update request for ${itemType} ${itemId} with data:`, data);
                
                // Add feedback to show we're saving
                contentField.classList.add('saving');
                
                // Send the update to the server
                fetch(`/team/update_item/${itemType}/${itemId}`, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => {
                    console.log(`Response status: ${response.status}`);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(`Response data:`, data);
                    contentField.classList.remove('saving');
                    
                    if (data.status === 'success') {
                        console.log(`${itemType} updated successfully`);
                        // Add a visual confirmation
                        contentField.style.backgroundColor = '#d4edda';
                        setTimeout(() => {
                            contentField.style.backgroundColor = '';
                        }, 1000);
                    } else {
                        console.error(`Error updating ${itemType}:`, data.message);
                        // Revert to original content if there was an error
                        contentField.innerText = originalContent;
                        contentField.style.backgroundColor = '#f8d7da';
                        setTimeout(() => {
                            contentField.style.backgroundColor = '';
                        }, 1000);
                    }
                    // Make the field non-editable again
                    contentField.contentEditable = 'false';
                })
                .catch(error => {
                    console.error(`Error updating ${itemType}:`, error);
                    contentField.classList.remove('saving');
                    
                    // Revert to original content
                    contentField.innerText = originalContent;
                    contentField.contentEditable = 'false';
                    contentField.style.backgroundColor = '#f8d7da';
                    setTimeout(() => {
                        contentField.style.backgroundColor = '';
                    }, 1000);
                });
            };
            
            // Add a one-time blur event listener
            const blurHandler = function() {
                // Remove the event listener first to prevent multiple calls
                contentField.removeEventListener('blur', blurHandler);
                saveContent();
            };
            
            contentField.addEventListener('blur', blurHandler);
            
            // Also save on Enter key (without shift)
            contentField.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    
                    // Remove focus to trigger blur event
                    contentField.blur();
                } else if (e.key === 'Escape') {
                    // Cancel editing on Escape
                    e.preventDefault();
                    contentField.innerText = originalContent;
                    contentField.contentEditable = 'false';
                    
                    // Remove the blur handler to prevent saving
                    contentField.removeEventListener('blur', blurHandler);
                }
            });
        };
        
        // Add the new click event listener
        btn.addEventListener('click', btn._clickHandler);
    });
}

// Handle AJAX form submissions with proper error handling
function setupAjaxFormSubmission() {
    $('.ajax-form').each(function() {
        const form = $(this);
        
        form.on('submit', function(e) {
            e.preventDefault();
            
            const submitButton = form.find('[type="submit"]');
            const originalButtonText = submitButton.html();
            
            // Disable the button and show loading
            submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Saving...');
            
            // Get the form data
            const formData = new FormData(this);
            
            // Send the AJAX request
            $.ajax({
                url: form.attr('action'),
                type: form.attr('method') || 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    // Handle success - check for redirect or update elements
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    } else if (response.refresh) {
                        window.location.reload();
                    } else if (response.html && response.targetId) {
                        $(response.targetId).html(response.html);
                    }
                    
                    // Show success message if provided
                    if (response.message) {
                        showNotification(response.message, 'success');
                    }
                    
                    // Reset form if needed
                    if (form.data('reset-on-success')) {
                        form[0].reset();
                    }
                    
                    // Close modal if the form is in a modal
                    const modal = form.closest('.modal');
                    if (modal.length) {
                        modal.modal('hide');
                    }
                },
                error: function(xhr) {
                    console.error('Form submission error:', xhr);
                    
                    let errorMessage = 'An error occurred. Please try again.';
                    
                    // Try to extract error message from response
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.message) {
                            errorMessage = response.message;
                        }
                    } catch (e) {
                        // If parsing failed, use default message
                    }
                    
                    showNotification(errorMessage, 'error');
                },
                complete: function() {
                    // Re-enable the button and restore original text
                    submitButton.prop('disabled', false).html(originalButtonText);
                }
            });
        });
    });
}

// Helper function to show notifications
function showNotification(message, type = 'success') {
    const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
    const bgColor = type === 'success' ? '#d4edda' : '#f8d7da';
    const textColor = type === 'success' ? '#155724' : '#721c24';
    
    const notification = $(`
        <div class="notification" style="position: fixed; top: 20px; right: 20px; z-index: 9999; padding: 15px 20px; 
        background-color: ${bgColor}; color: ${textColor}; border-radius: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        display: flex; align-items: center; max-width: 300px; animation: slideIn 0.3s ease;">
            <i class="fas ${iconClass} me-2"></i>
            <span>${message}</span>
        </div>
    `).appendTo('body');
    
    // Add CSS animation
    $('<style>')
        .text('@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }')
        .appendTo('head');
    
    // Remove notification after 5 seconds
    setTimeout(() => {
        notification.css('animation', 'slideOut 0.3s ease forwards');
        $('<style>')
            .text('@keyframes slideOut { from { transform: translateX(0); } to { transform: translateX(100%); opacity: 0; } }')
            .appendTo('head');
        
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Function to initialize all sortable lists on page load
function initAllSortables() {
    // Initialize todo sortable if on dashboard
    initTodoSortable();
    initPrioritiesSortable();
    
    // Initialize all member item sortables if on team page
    $('.member-select').each(function() {
        const memberId = $(this).data('member-id');
        if (memberId) {
            // If this member is selected (visible), set up sortable for their lists
            if ($(this).closest('.team-member-card').hasClass('selected')) {
                setupDragAndDrop('project', memberId);
                setupDragAndDrop('task', memberId);
                setupDragAndDrop('development', memberId);
            }
        }
    });
}

// Document ready handler for various functionalities
$(document).ready(function() {
    // Initialize color picker if on settings page
    setupColorPicker();
    
    // Handle embedded link clicks to open in new tab/window
    $('.external-link').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        window.open(url, '_blank');
    });
    
    // Toggle member details on all_members page
    $('.member-select').on('click', function(){
        // Hide all detail sections
        $('.member-content').hide();

        // Grab the ID of the clicked member
        const memberId = $(this).data('member-id');
        console.log("Clicked member ID:", memberId);

        // Remove selected class from all team members
        $('.team-member-card').removeClass('selected');
        
        // Add selected class to the clicked member
        $(this).closest('.team-member-card').addClass('selected');

        // Show the container for that member
        $('#member-content-' + memberId).slideDown();
        
        // Set up drag & drop for the currently viewed member
        setupDragAndDrop('project', memberId);
        setupDragAndDrop('task', memberId);
        setupDragAndDrop('development', memberId);
        
        // Enable inline editing for the currently viewed member items
        enableInlineEditing('project');
        enableInlineEditing('task');
        enableInlineEditing('development');
    });

    // If there's a hash in the URL, try to select that member
    if (window.location.hash) {
        const memberId = window.location.hash.substring(1);
        const memberSelect = $(`.member-select[data-member-id="${memberId}"]`);
        
        if (memberSelect.length) {
            memberSelect.click();
            
            // Scroll to the member's content
            $('html, body').animate({
                scrollTop: $('#member-content-' + memberId).offset().top - 100
            }, 500);
        }
    } else {
        // If no hash, and there's only one member, select them automatically
        const memberSelects = $('.member-select');
        if (memberSelects.length === 1) {
            memberSelects.click();
        }
    }

    // AJAX form submission for adding new tasks
    $('#addTaskFormContainer form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Refresh the todo list without full page reload
                refreshTodoList();
                
                // Clear the form
                $('#newTaskInput').val('');
                
                // Hide the form after submission
                $('#addTaskFormContainer').removeClass('show-form');
            },
            error: function(error) {
                console.error('Error adding task:', error);
                alert('Failed to add the task. Please try again.');
            }
        });
    });

    // Handle Edit Todo Modal submission via AJAX
    $('.edit-todo-form').on('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const modalId = $(this).closest('.modal').attr('id');
        
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Close the modal
                $(`#${modalId}`).modal('hide');
                
                // Update the todo item in the list without full page reload
                refreshTodoList();
            },
            error: function(error) {
                console.error('Error updating task:', error);
                alert('Failed to update the task. Please try again.');
            }
        });
    });
    
    // Initialize all sortable lists on page load
    initAllSortables();
    
    // Enable inline editing for various elements
    enableInlineEditing('project');
    enableInlineEditing('task');
    enableInlineEditing('development');
    
    // Setup AJAX form submissions
    setupAjaxFormSubmission();
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // When a modal is hidden (closed), immediately update the todo content
    $('.modal').on('hidden.bs.modal', function() {
        if ($(this).attr('id') && $(this).attr('id').startsWith('editTodoModal')) {
            // After editing a task and closing the modal, update the list
            $.get('/get_todos', function(data) {
                $('#dashboard-todo-list').html(data);
                initTodoSortable(); // Re-initialize sortable
            });
        } else if ($(this).attr('id') && (
            $(this).attr('id').includes('Project') || 
            $(this).attr('id').includes('Task') || 
            $(this).attr('id').includes('Development')
        )) {
            // After adding/editing items from modals, re-initialize sortables
            // Get member ID from URL hash or from modal ID
            let memberId = window.location.hash ? window.location.hash.substring(1) : null;
            
            if (!memberId) {
                // Try to extract from modal ID if possible
                const modalId = $(this).attr('id');
                if (modalId.includes('Modal')) {
                    memberId = modalId.replace(/\D/g, '');
                }
            }
            
            if (memberId) {
                setupDragAndDrop('project', memberId);
                setupDragAndDrop('task', memberId);
                setupDragAndDrop('development', memberId);
            }
        }
    });
});