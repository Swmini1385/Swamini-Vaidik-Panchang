/**
 * Swipe Navigation for Bootstrap Tabs
 * @param {string} contentAreaId - The ID of the container element that listens to swipe events
 * @param {string} tabsId - The ID of the ul/nav containing the Bootstrap tabs
 */
function initSwipeTabs(contentAreaId, tabsId) {
    const swipeContainer = document.getElementById(contentAreaId);
    const tabList = document.getElementById(tabsId);
    
    if (!swipeContainer || !tabList) return;

    let touchstartX = 0;
    let touchendX = 0;

    swipeContainer.addEventListener('touchstart', function(event) {
        touchstartX = event.changedTouches[0].screenX;
    }, {passive: true});

    swipeContainer.addEventListener('touchend', function(event) {
        touchendX = event.changedTouches[0].screenX;
        handleSwipe();
    }, {passive: true});

    function handleSwipe() {
        const diffX = touchendX - touchstartX;
        const SWIPE_THRESHOLD = 50;

        if (Math.abs(diffX) < SWIPE_THRESHOLD) return;

        // Get all tabs
        const tabs = Array.from(tabList.querySelectorAll('button[data-bs-toggle="tab"]'));
        if (tabs.length === 0) return;

        const activeTabIndex = tabs.findIndex(tab => tab.classList.contains('active'));
        
        if (diffX < 0) {
            // Swiped left -> Next tab
            if (activeTabIndex < tabs.length - 1) {
                applyAnimation('left');
                const nextTab = new bootstrap.Tab(tabs[activeTabIndex + 1]);
                nextTab.show();
                tabs[activeTabIndex + 1].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        } else {
            // Swiped right -> Previous tab
            if (activeTabIndex > 0) {
                applyAnimation('right');
                const prevTab = new bootstrap.Tab(tabs[activeTabIndex - 1]);
                prevTab.show();
                tabs[activeTabIndex - 1].scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        }
    }
    
    function applyAnimation(direction) {
        // Find the active tab panel
        const activePanel = document.querySelector('.tab-panel.active');
        if (activePanel) {
            // Remove any existing animation classes
            activePanel.classList.remove('slide-left', 'slide-right');
            
            // Force a reflow to restart animation
            void activePanel.offsetWidth;
            
            // Add the new animation class
            activePanel.classList.add(direction === 'left' ? 'slide-left' : 'slide-right');
        }
    }
}

// Add static CSS for these animations to the document if not present
if (!document.getElementById('swipe-tab-styles')) {
    const style = document.createElement('style');
    style.id = 'swipe-tab-styles';
    style.textContent = `
        .slide-left { animation: slideInRight 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; }
        .slide-right { animation: slideInLeft 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; }
    `;
    document.head.appendChild(style);
}
