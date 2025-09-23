document.addEventListener('DOMContentLoaded', function() {
    // Handle form submission with loading state
    const analyzeForm = document.getElementById('analyzeForm');
    if (analyzeForm) {
        analyzeForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('.analyze-btn');
            const btnText = submitBtn.querySelector('.btn-text');
            const spinner = submitBtn.querySelector('.loading-spinner');
            
            // Show loading state
            btnText.textContent = 'Analyzing...';
            spinner.style.display = 'inline-block';
            submitBtn.disabled = true;
            submitBtn.style.opacity = '0.8';
            
            // Validate input
            const topicInput = document.getElementById('topic');
            if (!topicInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a topic to analyze.');
                resetButton();
                return;
            }
            
            function resetButton() {
                btnText.textContent = 'Analyze Sentiment';
                spinner.style.display = 'none';
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
            }
        });
    }
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.info-card, .download-card, .viz-card, .feature');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Image modal functionality for visualizations
    const vizImages = document.querySelectorAll('.viz-image');
    vizImages.forEach(img => {
        img.addEventListener('click', function() {
            openImageModal(this.src, this.alt);
        });
        
        // Add cursor pointer to indicate clickability
        img.style.cursor = 'pointer';
    });
    
    function openImageModal(src, alt) {
        // Create modal overlay
        const modal = document.createElement('div');
        modal.className = 'image-modal';
        modal.innerHTML = `
            <div class="modal-overlay">
                <div class="modal-content">
                    <span class="modal-close">&times;</span>
                    <img src="${src}" alt="${alt}" class="modal-image">
                    <p class="modal-caption">${alt}</p>
                </div>
            </div>
        `;
        
        // Add modal styles
        const modalStyles = `
            .image-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 1000;
                animation: fadeIn 0.3s ease;
            }
            
            .modal-overlay {
                position: relative;
                max-width: 90%;
                max-height: 90%;
            }
            
            .modal-content {
                background: white;
                border-radius: 15px;
                padding: 20px;
                position: relative;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }
            
            .modal-close {
                position: absolute;
                top: 10px;
                right: 15px;
                font-size: 2rem;
                cursor: pointer;
                color: #666;
                z-index: 1001;
            }
            
            .modal-close:hover {
                color: #333;
            }
            
            .modal-image {
                max-width: 100%;
                max-height: 70vh;
                border-radius: 10px;
            }
            
            .modal-caption {
                text-align: center;
                margin-top: 15px;
                color: #666;
                font-weight: 500;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
        `;
        
        // Add styles to head if not already added
        if (!document.querySelector('#modal-styles')) {
            const styleSheet = document.createElement('style');
            styleSheet.id = 'modal-styles';
            styleSheet.textContent = modalStyles;
            document.head.appendChild(styleSheet);
        }
        
        document.body.appendChild(modal);
        
        // Close modal functionality
        const closeBtn = modal.querySelector('.modal-close');
        const overlay = modal.querySelector('.image-modal');
        
        closeBtn.addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                document.body.removeChild(modal);
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                document.body.removeChild(modal);
                document.removeEventListener('keydown', escapeHandler);
            }
        });
    }
    
    // Add download tracking
    const downloadLinks = document.querySelectorAll('.download-btn');
    downloadLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Add visual feedback
            const originalText = this.textContent;
            this.textContent = 'Downloading...';
            this.style.opacity = '0.7';
            
            setTimeout(() => {
                this.textContent = originalText;
                this.style.opacity = '1';
            }, 2000);
        });
    });
    
    // Add animation on scroll for results page
    if (window.location.pathname.includes('results') || document.querySelector('.results-content')) {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Observe all major sections
        const sections = document.querySelectorAll('.downloads-section, .visualizations-section, .report-section, .dataset-section');
        sections.forEach(section => {
            section.style.opacity = '0';
            section.style.transform = 'translateY(30px)';
            section.style.transition = 'all 0.6s ease';
            observer.observe(section);
        });
    }
    
    // Add copy to clipboard functionality for any code blocks
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy';
        copyBtn.className = 'copy-btn';
        copyBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: #3498db;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.8rem;
        `;
        
        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
        
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                }, 2000);
            });
        });
    });
});

