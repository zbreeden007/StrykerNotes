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
            setupDragAndDrop('project', memberId);
            setupDragAndDrop('task', memberId);
            setupDragAndDrop('development', memberId);
        }
        
        // Enable inline editing for this member's items
        if (typeof enableInlineEditing === 'function') {
            enableInlineEditing('project');
            enableInlineEditing('task');
            enableInlineEditing('development');
        }
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
    
    // Make project/task/development forms submit via AJAX
    $('.member-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(this);
        const submitButton = form.find('button[type="submit"]');
        const originalButtonText = submitButton.html();
        
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
                
                // Refresh the page to show new item
                // In a future enhancement, we could add the new item via JS without refreshing
                window.location.reload();
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
    
    // Update hash when tabs are changed
    $('.nav-tabs a').on('shown.bs.tab', function(e) {
        const memberId = $(e.target).data('member-id');
        if (memberId) {
            window.location.hash = memberId;
        }
    });
});