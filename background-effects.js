/**
 * WaterBuddy Background Effects
 * Handles 3D animations, parallax effects, and floating bubbles
 */

// Initialize effects when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Create parallax background container if doesn't exist
    if (!document.getElementById('parallaxBg')) {
        const parallaxBg = document.createElement('div');
        parallaxBg.id = 'parallaxBg';
        parallaxBg.className = 'parallax-bg';
        document.body.prepend(parallaxBg);
    }
    
    // Initialize effects
    createBubbles();
    initParallaxEffect();
});

// Create floating bubbles
function createBubbles() {
    const bubbleContainer = document.getElementById('parallaxBg');
    if (!bubbleContainer) return;
    
    const bubbleCount = 15;
    
    for(let i = 0; i < bubbleCount; i++) {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        
        // Random size
        const size = Math.random() * 60 + 20;
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        
        // Random position
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        bubble.style.left = `${posX}%`;
        bubble.style.top = `${posY}%`;
        
        // Random animation delay
        bubble.style.animationDelay = `${Math.random() * 5}s`;
        
        bubbleContainer.appendChild(bubble);
    }
}

// Parallax effect on mouse move
function initParallaxEffect() {
    document.addEventListener('mousemove', function(e) {
        const cards = document.querySelectorAll('.card-3d');
        const bubbles = document.querySelectorAll('.bubble');
        
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;
        
        // Move cards slightly based on mouse position
        cards.forEach(card => {
            const offsetX = (mouseX - 0.5) * 10; 
            const offsetY = (mouseY - 0.5) * 10;
            card.style.transform = `perspective(1000px) rotateY(${offsetX}deg) rotateX(${-offsetY}deg) translateZ(10px)`;
        });
        
        // Move bubbles in parallax effect
        bubbles.forEach((bubble, index) => {
            const depth = 0.5 + (index % 3) * 0.2; // Different depths for different bubbles
            const moveX = (mouseX - 0.5) * 40 * depth;
            const moveY = (mouseY - 0.5) * 40 * depth;
            bubble.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
        });
        
        // Subtle background parallax
        document.body.style.backgroundPosition = `${50 + mouseX * 5}% ${50 + mouseY * 5}%`;
    });
} 