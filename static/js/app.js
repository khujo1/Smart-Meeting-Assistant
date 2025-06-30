class MeetingProcessor {
    constructor() {
        console.log('MeetingProcessor starting...');
        console.log('Document ready state:', document.readyState);
        this.currentFile = null;
        this.currentSelectedMeetingId = null;
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('Initializing MeetingProcessor...');
        try {
            this.setupUploadHandlers();
            this.setupAdvancedFeatureHandlers();
            this.loadMeetings();
            console.log('MeetingProcessor initialized successfully');
        } catch (error) {
            console.error('Error initializing MeetingProcessor:', error);
        }
    }

    setupUploadHandlers() {
        console.log('Setting up upload handlers...');
        
        // Get elements
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
        const processBtn = document.getElementById('process-btn');

        console.log('Upload elements:', {
            fileInput: fileInput ? 'found' : 'not found',
            uploadArea: uploadArea ? 'found' : 'not found',
            processBtn: processBtn ? 'found' : 'not found'
        });

        if (!fileInput || !uploadArea) {
            console.error('Required upload elements not found');
            return;
        }

        // Store original upload area content ONLY if not already stored
        if (!this.originalUploadContent) {
            this.originalUploadContent = uploadArea.innerHTML;
            console.log('Original upload content stored');
        }

        // Remove any existing event listeners to prevent duplicates
        const newUploadArea = uploadArea.cloneNode(true);
        uploadArea.parentNode.replaceChild(newUploadArea, uploadArea);
        
        // Get the new elements after cloning
        const freshFileInput = document.getElementById('file-input');
        const freshUploadArea = document.getElementById('upload-area');

        // Simple direct click handler for upload area
        freshUploadArea.addEventListener('click', (e) => {
            console.log('Upload area clicked directly');
            e.preventDefault();
            e.stopPropagation();
            console.log('About to trigger file input click...');
            freshFileInput.click();
            console.log('File input click triggered');
        });

        // File selection handler
        freshFileInput.addEventListener('change', (e) => {
            console.log('File input change event:', e.target.files[0]);
            if (e.target.files[0]) {
                this.handleFileSelect(e);
            }
        });

        // Process button handler
        if (processBtn) {
            // Remove existing listeners
            const newProcessBtn = processBtn.cloneNode(true);
            processBtn.parentNode.replaceChild(newProcessBtn, processBtn);
            
            newProcessBtn.addEventListener('click', () => {
                console.log('Process button clicked');
                this.processFile();
            });
        }

        // Add drag and drop functionality
        freshUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            freshUploadArea.style.background = '#e3f2fd';
            console.log('Drag over');
        });

        freshUploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            freshUploadArea.style.background = '#f0f8ff';
            console.log('Drag leave');
        });

        freshUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            freshUploadArea.style.background = '#f0f8ff';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                console.log('File dropped:', files[0].name);
                freshFileInput.files = files;
                const event = new Event('change', { bubbles: true });
                freshFileInput.dispatchEvent(event);
            }
        });

        // Also handle the visible file input as backup
        const visibleFileInput = document.getElementById('visible-file-input');
        if (visibleFileInput) {
            visibleFileInput.addEventListener('change', (e) => {
                console.log('Visible file input changed:', e.target.files[0]);
                if (e.target.files[0]) {
                    // Copy the file to the hidden input
                    freshFileInput.files = e.target.files;
                    this.handleFileSelect(e);
                }
            });
        }

        console.log('Upload handlers set up successfully');
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        console.log('File selected:', file.name, file.size);

        // Basic validation
        const allowedTypes = ['audio/mp3', 'audio/wav', 'audio/m4a', 'audio/mpeg', 'audio/x-m4a'];
        if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a)$/i)) {
            alert('Please select a valid audio file (MP3, WAV, or M4A)');
            return;
        }

        const maxSize = 25 * 1024 * 1024; // 25MB
        if (file.size > maxSize) {
            alert('File size must be less than 25MB');
            return;
        }

        this.currentFile = file;
        
        // Update UI but preserve click functionality through event delegation
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.innerHTML = `
                <div class="file-selected" style="padding: 30px; text-align: center; cursor: pointer;">
                    <div class="file-icon" style="font-size: 48px; margin-bottom: 10px;">🎵</div>
                    <div class="file-info">
                        <p class="file-name" style="font-size: 18px; font-weight: bold; color: #1976D2;">${file.name}</p>
                        <p class="file-size" style="color: #666;">${this.formatFileSize(file.size)}</p>
                        <small style="color: #FF5722; text-decoration: underline;">Click to change file</small>
                    </div>
                </div>
            `;
        }

        // Show process button
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.style.display = 'block';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async processFile() {
        if (!this.currentFile) {
            alert('Please select a file first');
            return;
        }

        console.log('Processing file:', this.currentFile.name);

        // Show processing indicator
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.disabled = true;
            processBtn.innerHTML = 'Processing... <div class="spinner"></div>';
        }

        const formData = new FormData();
        formData.append('file', this.currentFile);

        try {
            // Step 1: Upload the file
            console.log('Step 1: Uploading file...');
            const uploadResponse = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const uploadData = await uploadResponse.json();
            console.log('Upload response:', uploadData);

            if (!uploadData.success) {
                throw new Error(uploadData.error || 'Upload failed');
            }

            // Step 2: Process the uploaded file
            console.log('Step 2: Processing uploaded file...');
            const processResponse = await fetch(`/process/${uploadData.filename}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: `Meeting - ${this.currentFile.name}`,
                    attendees: []
                })
            });

            const processData = await processResponse.json();
            console.log('Process response:', processData);

            if (processData.success) {
                alert('File processed successfully! Check the meetings list below.');
                this.loadMeetings(); // Refresh meetings list
                this.resetUploadSection();
            } else {
                throw new Error(processData.error || 'Processing failed');
            }

        } catch (error) {
            console.error('Processing error:', error);
            alert('Processing failed: ' + error.message);
        } finally {
            // Reset button state
            if (processBtn) {
                processBtn.disabled = false;
                processBtn.innerHTML = 'Process Meeting';
            }
        }
    }

    async loadMeetings() {
        console.log('Loading meetings...');
        try {
            const response = await fetch('/meetings');
            const data = await response.json();
            console.log('Meetings data:', data);
            
            if (data.meetings && data.meetings.length > 0) {
                this.displayMeetings(data.meetings);
            } else {
                this.showNoMeetings();
            }
        } catch (error) {
            console.error('Error loading meetings:', error);
            this.showNoMeetings();
        }
    }

    displayMeetings(meetings) {
        console.log('Displaying meetings:', meetings.length);
        const meetingsList = document.getElementById('meetings-list');
        
        if (!meetingsList) {
            console.error('meetings-list element not found');
            return;
        }

        console.log('meetings-list element found, updating content...');

        const meetingsHtml = meetings.map(meeting => {
            const title = meeting.filename || 'Untitled Meeting';
            const summary = meeting.analysis?.summary || meeting.summary || 'No summary available';
            const timestamp = meeting.timestamp ? new Date(meeting.timestamp).toLocaleString() : 'Unknown date';
            
            return `
                <div class="meeting-item" data-meeting-id="${meeting.id}" onclick="meetingProcessor.viewMeeting('${meeting.id}')" style="background: #e3f2fd; border: 2px solid #2196F3; margin: 10px 0; padding: 15px; border-radius: 8px; cursor: pointer;">
                    <div class="meeting-title" style="font-weight: bold; color: #1976D2; font-size: 16px; margin-bottom: 8px;">📋 ${title}</div>
                    <div class="meeting-summary" style="color: #555; margin-bottom: 8px;">${summary.substring(0, 100)}${summary.length > 100 ? '...' : ''}</div>
                    <div class="meeting-meta" style="color: #777; font-size: 12px;">📅 ${timestamp} | 🆔 ID: ${meeting.id}</div>
                </div>
            `;
        }).join('');
        
        meetingsList.innerHTML = `
            <div style="background: #4CAF50; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center;">
                ✅ ${meetings.length} Meeting(s) Loaded Successfully!
            </div>
            ${meetingsHtml}
        `;
        console.log('Meetings HTML updated:', meetingsHtml.length, 'characters');
    }

    showNoMeetings() {
        const meetingsList = document.getElementById('meetings-list');
        if (meetingsList) {
            meetingsList.innerHTML = '<p class="no-meetings">No meetings processed yet. Upload your first meeting recording above!</p>';
        }
    }

    async viewMeeting(meetingId) {
        console.log('Viewing meeting:', meetingId);
        try {
            const response = await fetch(`/meetings/${meetingId}`);
            const data = await response.json();
            
            if (data.meeting) {
                console.log('Meeting details:', data.meeting);
                this.showMeetingDetails(data.meeting);
            } else {
                alert('Meeting not found');
            }
        } catch (error) {
            console.error('Error loading meeting:', error);
            alert('Failed to load meeting: ' + error.message);
        }
    }

    showMeetingDetails(meeting) {
        // Create a modal or detailed view
        console.log('Full meeting object:', meeting);
        
        // Handle action items properly
        let actionItemsHtml = '';
        if (meeting.analysis?.action_items) {
            const actionItems = meeting.analysis.action_items;
            console.log('Action items:', actionItems);
            
            if (Array.isArray(actionItems)) {
                actionItemsHtml = actionItems.map(item => {
                    // Handle both string and object action items
                    const itemText = typeof item === 'string' ? item : (item.text || item.description || JSON.stringify(item));
                    return `<li style="margin-bottom: 8px;">${itemText}</li>`;
                }).join('');
            } else if (typeof actionItems === 'string') {
                actionItemsHtml = `<li style="margin-bottom: 8px;">${actionItems}</li>`;
            } else {
                actionItemsHtml = `<li style="margin-bottom: 8px;">Action items available but format unclear</li>`;
            }
        }

        // Handle key points properly
        let keyPointsHtml = '';
        if (meeting.analysis?.key_points) {
            const keyPoints = meeting.analysis.key_points;
            console.log('Key points:', keyPoints);
            
            if (Array.isArray(keyPoints)) {
                keyPointsHtml = keyPoints.map(point => {
                    const pointText = typeof point === 'string' ? point : (point.text || point.description || JSON.stringify(point));
                    return `<li style="margin-bottom: 8px;">${pointText}</li>`;
                }).join('');
            } else if (typeof keyPoints === 'string') {
                keyPointsHtml = `<li style="margin-bottom: 8px;">${keyPoints}</li>`;
            }
        }

        const detailsHtml = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; display: flex; align-items: center; justify-content: center;" id="meeting-details-modal">
                <div style="background: white; padding: 30px; border-radius: 15px; max-width: 800px; max-height: 80vh; overflow-y: auto; margin: 20px;">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 15px;">
                        <h2 style="margin: 0; color: #1976D2;">📋 ${meeting.filename || 'Untitled Meeting'}</h2>
                        <button onclick="document.getElementById('meeting-details-modal').remove()" style="background: #f44336; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 20px;">✕ Close</button>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #2E7D32; margin-bottom: 10px;">📝 Summary</h3>
                        <p style="background: #f8f9fa; padding: 15px; border-radius: 8px; line-height: 1.6; border-left: 4px solid #4CAF50;">
                            ${meeting.analysis?.summary || meeting.summary || 'No summary available'}
                        </p>
                    </div>

                    ${keyPointsHtml ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #1976D2; margin-bottom: 10px;">🎯 Key Points</h3>
                        <ul style="background: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                            ${keyPointsHtml}
                        </ul>
                    </div>
                    ` : ''}

                    ${actionItemsHtml ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #FF5722; margin-bottom: 10px;">✅ Action Items</h3>
                        <ul style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #FF5722;">
                            ${actionItemsHtml}
                        </ul>
                    </div>
                    ` : ''}

                    ${meeting.transcript ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #9C27B0; margin-bottom: 10px;">📜 Transcript</h3>
                        <div style="background: #fafafa; padding: 15px; border-radius: 8px; max-height: 300px; overflow-y: auto; border-left: 4px solid #9C27B0; font-family: monospace; font-size: 14px; line-height: 1.5;">
                            ${meeting.transcript}
                        </div>
                    </div>
                    ` : ''}

                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
                        <p><strong>📅 Date:</strong> ${meeting.timestamp ? new Date(meeting.timestamp).toLocaleString() : 'Unknown'}</p>
                        <p><strong>🆔 ID:</strong> ${meeting.id}</p>
                        ${meeting.filename ? `<p><strong>📁 File:</strong> ${meeting.filename}</p>` : ''}
                    </div>
                </div>
            </div>
        `;
        
        // Remove any existing modal
        const existingModal = document.getElementById('meeting-details-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add the modal to the page
        document.body.insertAdjacentHTML('beforeend', detailsHtml);
    }

    setupAdvancedFeatureHandlers() {
        console.log('Setting up advanced feature handlers...');
        
        // Calendar & Task Integration buttons
        const createCalendarBtn = document.getElementById('create-calendar-btn');
        const createTasksBtn = document.getElementById('create-tasks-btn');
        const getInsightsBtn = document.getElementById('get-insights-btn');

        if (createCalendarBtn) {
            createCalendarBtn.addEventListener('click', () => this.createCalendarEvents());
        }

        if (createTasksBtn) {
            createTasksBtn.addEventListener('click', () => this.createTaskAssignments());
        }

        if (getInsightsBtn) {
            getInsightsBtn.addEventListener('click', () => this.getCrossMeetingInsights());
        }

        console.log('Advanced feature handlers set up');
    }

    async createCalendarEvents() {
        console.log('Creating calendar events...');
        try {
            const response = await fetch('/api/bulk-calendar-events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ Successfully created ${data.events_created || 0} calendar events!`);
            } else {
                alert('❌ Failed to create calendar events: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Calendar events error:', error);
            alert('❌ Error creating calendar events: ' + error.message);
        }
    }

    async createTaskAssignments() {
        console.log('Creating task assignments...');
        try {
            const response = await fetch('/api/bulk-task-assignments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(`✅ Successfully created ${data.tasks_created || 0} task assignments!`);
            } else {
                alert('❌ Failed to create task assignments: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Task assignments error:', error);
            alert('❌ Error creating task assignments: ' + error.message);
        }
    }

    async getCrossMeetingInsights() {
        console.log('Getting cross-meeting insights...');
        try {
            const response = await fetch('/api/insights');
            const data = await response.json();
            
            if (data.success && data.insights) {
                this.showInsightsModal(data.insights);
            } else {
                alert('❌ Failed to get insights: ' + (data.error || 'No insights available'));
            }
        } catch (error) {
            console.error('Cross-meeting insights error:', error);
            alert('❌ Error getting insights: ' + error.message);
        }
    }

    showInsightsModal(insights) {
        const insightsHtml = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000; display: flex; align-items: center; justify-content: center;" id="insights-modal">
                <div style="background: white; padding: 30px; border-radius: 15px; max-width: 900px; max-height: 80vh; overflow-y: auto; margin: 20px;">
                    <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 15px;">
                        <h2 style="margin: 0; color: #1976D2;">📊 Cross-Meeting Analytics</h2>
                        <button onclick="document.getElementById('insights-modal').remove()" style="background: #f44336; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 20px;">✕ Close</button>
                    </div>
                    
                    ${insights.patterns ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #2E7D32; margin-bottom: 10px;">🔄 Recurring Patterns</h3>
                        <ul style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50;">
                            ${insights.patterns.map(pattern => `<li style="margin-bottom: 8px;">${pattern}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}

                    ${insights.trends ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #1976D2; margin-bottom: 10px;">📈 Trends</h3>
                        <ul style="background: #f0f8ff; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                            ${insights.trends.map(trend => `<li style="margin-bottom: 8px;">${trend}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}

                    ${insights.recommendations ? `
                    <div style="margin-bottom: 20px;">
                        <h3 style="color: #FF5722; margin-bottom: 10px;">💡 Recommendations</h3>
                        <ul style="background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #FF5722;">
                            ${insights.recommendations.map(rec => `<li style="margin-bottom: 8px;">${rec}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}

                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee; color: #666; font-size: 14px;">
                        <p><strong>📅 Analysis Date:</strong> ${new Date().toLocaleString()}</p>
                        <p><strong>📊 Meetings Analyzed:</strong> ${insights.meetings_count || 'N/A'}</p>
                    </div>
                </div>
            </div>
        `;
        
        // Remove any existing modal
        const existingModal = document.getElementById('insights-modal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add the modal to the page
        document.body.insertAdjacentHTML('beforeend', insightsHtml);
    }

    resetUploadSection() {
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea) {
            uploadArea.style.cursor = 'pointer';
            uploadArea.style.border = '4px dashed #FF0000';
            uploadArea.style.background = '#FFEEEE';
            uploadArea.style.padding = '20px';
            uploadArea.style.minHeight = '150px';
            uploadArea.style.display = 'flex';
            uploadArea.style.alignItems = 'center';
            uploadArea.style.justifyContent = 'center';
            uploadArea.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 48px; margin-bottom: 10px;">📤⬆️📂</div>
                    <div style="font-size: 24px; font-weight: bold; color: #FF0000; margin-bottom: 10px;">CLICK HERE TO UPLOAD!</div>
                    <div style="font-size: 18px; color: #FF5722;">Or drag and drop your audio file</div>
                    <div style="font-size: 14px; color: #666; margin-top: 10px;">MP3, WAV, M4A (max 25MB)</div>
                </div>
            `;
        }
        
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.style.display = 'none';
        }
        
        this.currentFile = null;
        
        // Re-setup upload handlers after resetting HTML
        this.setupUploadHandlers();
    }

    resetUploadArea() {
        const uploadArea = document.getElementById('upload-area');
        if (uploadArea && this.originalUploadContent) {
            uploadArea.innerHTML = this.originalUploadContent;
        }
        this.currentFile = null;
        
        // Hide process button
        const processBtn = document.getElementById('process-btn');
        if (processBtn) {
            processBtn.style.display = 'none';
        }
    }
}

// Global test function for debugging
window.testFilePicker = function() {
    console.log('Test file picker called');
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        console.log('File input found, triggering click...');
        fileInput.click();
        console.log('Click triggered');
    } else {
        console.log('File input NOT found');
    }
};

// Initialize the application
console.log('app.js loaded successfully!');
console.log('Initializing meeting processor...');
const meetingProcessor = new MeetingProcessor();
