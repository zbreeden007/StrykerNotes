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

// Function to refresh the todo list via AJAX
function refreshTodoList() {
    $.ajax({
        url: '/get_todos', // You'll need to create this endpoint
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
        if (todoList.sortable) {
            todoList.sortable.destroy();
        }
        
        new Sortable(todoList, {
            animation: 150,
            handle: '.handle',
            ghostClass: 'sortable-ghost',
            onEnd: function(evt) {
                const todoIds = Array.from(todoList.children)
                    .map(item => item.id.replace('todo-', ''));
                
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
                    if (data.status !== 'success') {
                        console.error('Error reordering todos:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error reordering todos:', error);
                });
            }
        });
    }
}

// Update this function to account for member-specific lists
function setupDragAndDrop(itemType, memberId) {
    const container = document.getElementById(`${itemType}-list-${memberId}`);
    if (!container) {
        console.error(`Container not found for ${itemType}-list-${memberId}`);
        return;
    }
    
    console.log(`Setting up drag and drop for ${itemType}-list-${memberId}`);
    console.log(`Found ${container.children.length} ${itemType} items`);

    new Sortable(container, {
        animation: 150,
        onEnd: function (evt) {
            const itemOrder = Array.from(container.children)
                .map(item => {
                    console.log(`Item in ${itemType} list:`, item);
                    return item.dataset.itemId;
                });
            
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
                console.log(`Reorder response status: ${response.status}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(`Reorder response data:`, data);
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
}

function enableInlineEditing(itemType) {
    console.log(`Setting up inline editing for ${itemType} items`);
    const editButtons = document.querySelectorAll(`.${itemType}-edit`);
    console.log(`Found ${editButtons.length} ${itemType} edit buttons`);
    
    editButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            console.log(`Edit button clicked for ${itemType} with ID: ${itemId}`);
            
            const contentField = document.getElementById(`${itemType}-content-${itemId}`);
            if (!contentField) {
                console.error(`Content field not found for ${itemType}-content-${itemId}`);
                return;
            }
            console.log(`Content field found: ${contentField.innerText}`);

            // Make the field editable
            contentField.contentEditable = 'true';
            contentField.focus();
            
            // Store original content in case we need to revert
            const originalContent = contentField.innerText;
            console.log(`Original content: ${originalContent}`);
            
            // Function to save the content
            const saveContent = function() {
                const updatedContent = contentField.innerText;
                console.log(`Updated content: ${updatedContent}`);
                
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
                    return response.json();
                })
                .then(data => {
                    console.log(`Response data:`, data);
                    if (data.status === 'success') {
                        console.log(`${itemType} updated successfully`);
                        // Add a visual confirmation
                        const tempHighlight = contentField.style.backgroundColor;
                        contentField.style.backgroundColor = '#d4edda';
                        setTimeout(() => {
                            contentField.style.backgroundColor = tempHighlight;
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
                    // Revert to original content
                    contentField.innerText = originalContent;
                    contentField.contentEditable = 'false';
                    contentField.style.backgroundColor = '#f8d7da';
                    setTimeout(() => {
                        contentField.style.backgroundColor = '';
                    }, 1000);
                });
            };
            
            // Save on blur
            contentField.addEventListener('blur', saveContent, { once: true });
            
            // Also save on Enter key
            contentField.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    contentField.blur(); // Trigger the blur event which saves the content
                }
            });
        });
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

        // Show the container for that member
        $('#member-content-' + memberId).slideDown();
    });

    // Setup the toggle functionality for the add task form
    $('#toggleAddTask').on('click', function(e) {
        e.preventDefault();
        console.log("Toggle Add Task clicked");
        $('#addTaskFormContainer').toggleClass('d-none');
        
        // Focus the input field if the form is now visible
        if (!$('#addTaskFormContainer').hasClass('d-none')) {
            $('#newTaskInput').focus();
        }
    });

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
                $('#addTaskFormContainer').addClass('d-none');
            },
            error: function(error) {
                console.error('Error adding task:', error);
                alert('Failed to add the task. Please try again.');
            }
        });
    });

    // Handle Edit Todo Modal submission via AJAX
    $('.modal form').on('submit', function(e) {
        // Only intercept task edit forms
        if ($(this).attr('action').includes('/todo/') && $(this).attr('action').includes('/edit')) {
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
        }
    });
    
    // Initialize todo sortable
    initTodoSortable();
    
    // Enable inline editing for various elements
    enableInlineEditing('project');
    enableInlineEditing('task');
    enableInlineEditing('development');
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize priorities container sortable
    const prioritiesContainer = document.getElementById('priorities-container');
    if (prioritiesContainer) {
        new Sortable(prioritiesContainer, {
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
    }
    
    // When a modal is hidden (closed), immediately update the todo content
    $('.modal').on('hidden.bs.modal', function() {
        if ($(this).attr('id') && $(this).attr('id').startsWith('editTodoModal')) {
            // After editing a task and closing the modal, update the list
            $.get('/get_todos', function(data) {
                $('#dashboard-todo-list').html(data);
            });
        }
    });
});