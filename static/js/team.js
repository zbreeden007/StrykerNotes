// Handle team member specific functionality
$(document).ready(function() {
    // Toggle member selection and show their details
    $('.member-select').on('click', function() {
        // Remove selected class from all team members
        $('.team-member-card').removeClass('selected');
        
        // Add selected class to the clicked member
        $(this).closest('.team-member-card').addClass('selected');
        
        // Hide all member content
        $('.member-content').hide();
        
        // Get member ID and show their content
        const memberId = $(this).data('member-id');
        $('#member-content-' + memberId).fadeIn();
        
        // Set up drag and drop for this member's lists
        if (typeof setupDragAndDrop === 'function') {
            console.log("Setting up drag and drop for member:", memberId);
            setupDragAndDrop('project', memberId);
            setupDragAndDrop('task', memberId);
            setupDragAndDrop('development', memberId);
        } else {
            console.error("setupDragAndDrop function not available");
        }
        
        // Enable inline editing for this member's items
        if (typeof enableInlineEditing === 'function') {
            enableInlineEditing('project');
            enableInlineEditing('task');
            enableInlineEditing('development');
        } else {
            console.error("enableInlineEditing function not available");
        }
        
        // Store the active member ID in session storage
        sessionStorage.setItem('activeMemberId', memberId);
    });
    
    // On page load, try to restore the previously active member
    const restoreActiveMember = function() {
        // First check URL hash
        let memberId = window.location.hash ? window.location.hash.substring(1) : null;
        
        // If no hash, check session storage
        if (!memberId) {
            memberId = sessionStorage.getItem('activeMemberId');
        }
        
        // If we have a member ID, select that member
        if (memberId) {
            const memberSelect = $(`.member-select[data-member-id="${memberId}"]`);
            if (memberSelect.length) {
                memberSelect.click();
                
                // Scroll to the member's content
                $('html, body').animate({
                    scrollTop: $('#member-content-' + memberId).offset().top - 100
                }, 500);
                
                return true;
            }
        }
        
        // If no stored member or hash, and there's only one member, select them automatically
        const memberSelects = $('.member-select');
        if (memberSelects.length === 1) {
            memberSelects.click();
            return true;
        }
        
        return false;
    };
    
    // Call the restore function
    restoreActiveMember();
    
    // Initialize sortable lists for any already visible member content
    $('.member-content').each(function() {
        if ($(this).is(':visible')) {
            const memberId = $(this).attr('id').replace('member-content-', '');
            if (typeof setupDragAndDrop === 'function') {
                console.log("Setting up initial drag and drop for visible member:", memberId);
                setupDragAndDrop('project', memberId);
                setupDragAndDrop('task', memberId);
                setupDragAndDrop('development', memberId);
            }
        }
    });
    
    // AJAX form submission for project, task, and development forms
    // Modified to update the DOM without page refresh
    $('.member-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(this);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.html();
        const modalId = form.closest('.modal').attr('id');
        const memberId = modalId.match(/\d+/)[0]; // Extract member ID from modal ID
        
        // Determine the type of form from the modal ID
        let itemType = '';
        if (modalId.includes('Project')) itemType = 'project';
        else if (modalId.includes('Task')) itemType = 'task';
        else if (modalId.includes('Development')) itemType = 'development';
        
        // Disable submit button and show loading
        submitButton.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i>');
        
        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                // Close the modal
                form.closest('.modal').modal('hide');
                
                // Reset the form for next use
                form[0].reset();
                
                // Instead of reloading, fetch the updated list via AJAX
                $.ajax({
                    url: `/team/fetch_items/${itemType}/${memberId}`,
                    type: 'GET',
                    success: function(htmlResponse) {
                        // Replace the list content with the updated HTML
                        $(`#${itemType}-list-${memberId}`).html(htmlResponse);
                        
                        // Re-initialize drag and drop for the updated list
                        if (typeof setupDragAndDrop === 'function') {
                            setupDragAndDrop(itemType, memberId);
                        }
                        
                        // Re-enable inline editing for the updated items
                        if (typeof enableInlineEditing === 'function') {
                            enableInlineEditing(itemType);
                        }
                        
                        // Show success notification
                        showNotification(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} added successfully!`, 'success');
                    },
                    error: function() {
                        // If fetching the updated list fails, just reload the page
                        window.location.hash = memberId;
                        window.location.reload();
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Error submitting form:', error);
                
                // Show error message
                const errorMessage = $('<div class="alert alert-danger mt-2"></div>')
                    .text('Error: ' + (xhr.responseJSON?.message || 'Failed to submit form'));
                
                form.prepend(errorMessage);
                
                // Remove error message after 5 seconds
                setTimeout(() => {
                    errorMessage.fadeOut(300, function() {
                        $(this).remove();
                    });
                }, 5000);
            },
            complete: function() {
                // Re-enable button and restore text
                submitButton.prop('disabled', false).html(originalButtonText);
            }
        });
    });
    
    // Intercept delete forms to use AJAX instead of page refresh
    $(document).on('submit', 'form[action*="delete_member_project"], form[action*="delete_member_task"], form[action*="delete_member_development"]', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const url = form.attr('action');
        const listItem = form.closest('li');
        const memberId = sessionStorage.getItem('activeMemberId');
        
        // Determine item type from the URL
        let itemType = '';
        if (url.includes('project')) itemType = 'project';
        else if (url.includes('task')) itemType = 'task';
        else if (url.includes('development')) itemType = 'development';
        
        // Show confirmation dialog
        if (confirm('Are you sure you want to delete this item?')) {
            // Add loading state
            listItem.css('opacity', '0.5');
            
            $.ajax({
                url: url,
                type: 'POST',
                success: function() {
                    // Animate the removal of the item
                    listItem.slideUp(300, function() {
                        $(this).remove();
                        
                        // Show empty message if list is now empty
                        const list = $(`#${itemType}-list-${memberId}`);
                        if (list.children().length === 0) {
                            list.parent().html('<p class="text-muted">No ' + itemType + 's added yet.</p>');
                        }
                        
                        // Re-initialize drag and drop for the updated list
                        if (typeof setupDragAndDrop === 'function' && list.children().length > 0) {
                            setupDragAndDrop(itemType, memberId);
                        }
                    });
                    
                    // Show success notification
                    showNotification(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} deleted successfully!`, 'success');
                },
                error: function() {
                    // If AJAX delete fails, remove loading state and show error
                    listItem.css('opacity', '1');
                    showNotification('Error deleting item. Please try again.', 'error');
                }
            });
        }
    });
    
    // Update hash when tabs are changed
    $('.nav-tabs a').on('shown.bs.tab', function(e) {
        const memberId = $(e.target).data('member-id');
        if (memberId) {
            window.location.hash = memberId;
            sessionStorage.setItem('activeMemberId', memberId);
        }
    });
    
    // Helper function to show notifications
    function showNotification(message, type = 'success') {
        // Check if showNotification exists in the global scope
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type);
            return;
        }
        
        // Fallback implementation if the global function doesn't exist
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
});