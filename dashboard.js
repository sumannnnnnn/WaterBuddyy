/**
 * WaterBuddy Dashboard Functionality
 * Handles water intake tracking, visualization, and calendar functionality
 */

class WaterDashboard {
    constructor() {
        // Initialize properties
        this.currentAmount = 0;
        this.goalAmount = 0;
        this.calendarData = {};
        this.currentDate = new Date();
        
        // DOM elements
        this.waterFill = document.getElementById('waterFill');
        this.currentAmountEl = document.getElementById('currentAmount');
        this.goalAmountEl = document.getElementById('goalAmount');
        this.calendarDays = document.getElementById('calendarDays');
        this.currentMonthEl = document.getElementById('currentMonth');
        this.currentStreakEl = document.getElementById('currentStreak');
        this.bestStreakEl = document.getElementById('bestStreak');
        
        // Load initial data
        this.loadInitialData();
        this.setupEventListeners();
    }
    
    loadInitialData() {
        // Get data from the page (set by Flask template)
        try {
            this.currentAmount = parseInt(this.currentAmountEl.textContent) || 0;
            this.goalAmount = parseInt(this.goalAmountEl.textContent) || 0;
            this.calendarData = window.calendarData || {};
            
            // Initialize visualization
            this.updateWaterFill();
            this.renderCalendar(this.currentDate);
            this.updateStreaks();
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    setupEventListeners() {
        // Add water buttons
        document.querySelectorAll('.add-water-btn').forEach(button => {
            button.addEventListener('click', () => {
                const amount = parseInt(button.getAttribute('data-amount'));
                this.addWater(amount);
            });
        });
        
        // Custom amount button
        const addCustomBtn = document.getElementById('addCustom');
        if (addCustomBtn) {
            addCustomBtn.addEventListener('click', () => {
                const customAmount = parseInt(document.getElementById('customAmount').value);
                if (customAmount > 0) {
                    this.addWater(customAmount);
                    document.getElementById('customAmount').value = '';
                }
            });
        }
        
        // Calendar navigation
        const prevMonthBtn = document.getElementById('prevMonth');
        const nextMonthBtn = document.getElementById('nextMonth');
        
        if (prevMonthBtn) {
            prevMonthBtn.addEventListener('click', () => {
                this.currentDate.setMonth(this.currentDate.getMonth() - 1);
                this.renderCalendar(this.currentDate);
            });
        }
        
        if (nextMonthBtn) {
            nextMonthBtn.addEventListener('click', () => {
                this.currentDate.setMonth(this.currentDate.getMonth() + 1);
                this.renderCalendar(this.currentDate);
            });
        }
    }
    
    updateWaterFill() {
        if (!this.waterFill || !this.currentAmountEl || !this.goalAmountEl) return;
        
        const percentage = Math.min((this.currentAmount / this.goalAmount) * 100, 100);
        this.waterFill.style.height = `${percentage}%`;
        this.currentAmountEl.textContent = this.currentAmount;
        this.goalAmountEl.textContent = this.goalAmount;
        
        // Add animation class if goal reached
        if (percentage >= 100 && !this.waterFill.classList.contains('goal-reached')) {
            this.waterFill.classList.add('goal-reached');
            this.celebrateGoalReached();
        }
    }
    
    async addWater(amount) {
        try {
            const response = await fetch('/add_water', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount: amount }),
            });
            
            const data = await response.json();
            if (data.success) {
                this.currentAmount = data.current_amount;
                this.goalAmount = data.goal;
                this.updateWaterFill();
                
                // Add a system message to chat if chatbot is initialized
                if (window.waterChatbot) {
                    window.waterChatbot.addSystemMessage(`Added ${amount}ml of water. Total: ${this.currentAmount}ml`);
                }
                
                // Update calendar for today
                const today = new Date().toISOString().split('T')[0];
                this.calendarData[today] = {
                    amount: this.currentAmount,
                    goal: this.goalAmount,
                    achieved: data.goal_achieved
                };
                
                // Refresh calendar
                this.renderCalendar(this.currentDate);
                this.updateStreaks();
            }
        } catch (error) {
            console.error('Error adding water:', error);
        }
    }
    
    renderCalendar(date) {
        if (!this.calendarDays || !this.currentMonthEl) return;
        
        const year = date.getFullYear();
        const month = date.getMonth();
        
        // Update month display
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        this.currentMonthEl.textContent = `${monthNames[month]} ${year}`;
        
        // Get first day of month and number of days
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        // Clear previous calendar days
        this.calendarDays.innerHTML = '';
        
        // Add empty cells for days before the first day of month
        for (let i = 0; i < firstDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day empty';
            this.calendarDays.appendChild(emptyDay);
        }
        
        // Add days of the month
        const today = new Date();
        const todayDate = today.getDate();
        const todayMonth = today.getMonth();
        const todayYear = today.getFullYear();
        
        for (let i = 1; i <= daysInMonth; i++) {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'calendar-day';
            dayDiv.textContent = i;
            
            // Check if this is today
            if (i === todayDate && month === todayMonth && year === todayYear) {
                dayDiv.classList.add('today');
            }
            
            // Check if this day has data in calendarData
            const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
            if (this.calendarData[dateStr] && this.calendarData[dateStr].achieved) {
                dayDiv.classList.add('achieved');
                dayDiv.title = `${this.calendarData[dateStr].amount}ml / ${this.calendarData[dateStr].goal}ml`;
            } else if (this.calendarData[dateStr]) {
                dayDiv.title = `${this.calendarData[dateStr].amount}ml / ${this.calendarData[dateStr].goal}ml`;
            }
            
            this.calendarDays.appendChild(dayDiv);
        }
    }
    
    updateStreaks() {
        if (!this.currentStreakEl || !this.bestStreakEl) return;
        
        // Calculate current streak
        let currentStreak = 0;
        let bestStreak = 0;
        let tempStreak = 0;
        
        const today = new Date();
        
        // Check backwards from today
        for (let i = 0; i < 365; i++) { // Check up to a year back
            const checkDate = new Date(today);
            checkDate.setDate(today.getDate() - i);
            const dateStr = checkDate.toISOString().split('T')[0];
            
            if (this.calendarData[dateStr] && this.calendarData[dateStr].achieved) {
                if (i === currentStreak) { // Only increment if consecutive
                    currentStreak++;
                }
                tempStreak++;
            } else {
                // Break streak
                bestStreak = Math.max(bestStreak, tempStreak);
                if (i <= currentStreak) { // Only reset current if we're still counting it
                    break;
                }
                tempStreak = 0;
            }
        }
        
        bestStreak = Math.max(bestStreak, tempStreak, currentStreak);
        
        this.currentStreakEl.textContent = currentStreak;
        this.bestStreakEl.textContent = bestStreak;
    }
    
    celebrateGoalReached() {
        // Create a celebration notification if goal just reached
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-bounce';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-trophy mr-2"></i>
                <span>Congratulations! You've reached your water goal for today!</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity', 'duration-500');
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the dashboard page
    if (document.getElementById('waterFill')) {
        // Make dashboard instance available globally
        window.waterDashboard = new WaterDashboard();
        
        // Expose methods for use by other scripts
        window.updateWaterFill = () => window.waterDashboard.updateWaterFill();
        window.renderCalendar = (date) => window.waterDashboard.renderCalendar(date);
        window.updateStreaks = () => window.waterDashboard.updateStreaks();
        window.currentDate = window.waterDashboard.currentDate;
    }
});