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
        
        // Update the hash without triggering scroll
        const scrollPos = $(window).scrollTop();
        window.location.hash = memberId;
        $(window).scrollTop(scrollPos);
    });
    
    // Handle hash in URL on page load
    function handleUrlHash() {
        if (window.location.hash) {
            const memberId = window.location.hash.substring(1);
            const memberSelect = $(`.member-select[data-member-id="${memberId}"]`);
            
            if (memberSelect.length) {
                // Wait a short moment for the page to fully render
                setTimeout(() => {
                    // Click the member to show their content
                    memberSelect.click();
                    
                    // Scroll to the member's content
                    $('html, body').animate({
                        scrollTop: $('#member-content-' + memberId).offset().top - 100
                    }, 300);
                }, 100);
                return true;
            }
        }
        
        // If no hash, and there's only one member, select them automatically
        const memberSelects = $('.member-select');
        if (memberSelects.length === 1) {
            memberSelects.click();
            return true;
        }
        
        return false;
    }
    
    // Make sure forms include the current hash
    $('form').on('submit', function() {
        // If there's no action attribute, don't modify
        if (!$(this).attr('action')) return;
        
        // If we have a hash, add it to the action
        if (window.location.hash) {
            // Create a hidden input field for the form
            $('<input>').attr({
                type: 'hidden',
                name: 'active_member',
                value: window.location.hash.substring(1)
            }).appendTo($(this));
        }
    });
    
    // Handle hash in URL after DOM is fully loaded
    $(window).on('load', function() {
        handleUrlHash();
    });
    
    // Ensure hash is processed immediately as well
    handleUrlHash();
});