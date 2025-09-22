import reflex as rx
import hashlib
from websiteanalytics.firebase.firebase_config import db
import time
from datetime import datetime

class AnalyticsState(rx.State):
    session_id: str = ""
    current_page: str = ""
    page_start_time: float = 0
    login_time: float = 0
    current_user: str = ""

    def start_session(self, user_email: str):
        self.session_id = f"{user_email}_{int(time.time())}"
        self.login_time = time.time()
        self.current_user = user_email
        
        print(f"Starting new session: {self.session_id} for user: {user_email}")

        db.collection("analytics").document(self.session_id).set({
            "user_email": user_email,
            "login_time": self.login_time,
            "session_start": time.time()
        })
    
    def start_page_tracking(self, page_name: str, user_email: str):
        if not self.session_id or self.current_user != user_email:
            print(f"New user or no session. Starting session for: {user_email}")
            self.start_session(user_email)
            
        if self.current_page and self.page_start_time:
            print(f"Saving time for previous page: {self.current_page}")
            self._save_page_time(user_email)
        
        self.current_page = page_name
        self.page_start_time = time.time()
        print(f"Starting tracking for page: {page_name}, user: {user_email}")
        self._record_page_visit(page_name, user_email)

    def _save_page_time(self, user_email: str):
        if not self.session_id:
            print("No session_id, cannot save page time")
            return
            
        time_spent_seconds = time.time() - self.page_start_time
        time_spent_minutes = round(time_spent_seconds / 60, 2)
        
        print(f"Saving page time: {self.current_page} = {time_spent_minutes} minutes")
        
        try:
            db.collection("analytics").document(self.session_id).set({
                f"pages.{self.current_page}.time_spent_minutes": time_spent_minutes,
                f"pages.{self.current_page}.exit_time": time.time()
            }, merge=True)
            print(f"Successfully saved page time for {self.current_page}")
        except Exception as e:
            print(f"Error saving page time: {e}")
    
    def _record_page_visit(self, page_name: str, user_email: str):
        if not self.session_id:
            print("No session_id, cannot record page visit")
            return
            
        try:
            doc = db.collection("analytics").document(self.session_id).get()
            current_visits = 0
            if doc.exists:
                data = doc.to_dict()
                current_visits = data.get("pages", {}).get(page_name, {}).get("visits", 0)
            
            db.collection("analytics").document(self.session_id).set({
                f"pages.{page_name}.visits": current_visits + 1,
                f"pages.{page_name}.entry_time": time.time(),
                f"pages.{page_name}.page_name": page_name
            }, merge=True)
            
            print(f"Recorded visit for {page_name}, visits: {current_visits + 1}")
            
        except Exception as e:
            print(f"Error recording page visit: {e}")
    
    def end_session(self, user_email: str):
        if not self.session_id:
            print("No session to end")
            return
            
        try:
            if self.current_page and self.page_start_time:
                self._save_page_time(user_email)
            
            total_time_seconds = time.time() - self.login_time
            total_time_minutes = round(total_time_seconds / 60, 2)
            
            db.collection("analytics").document(self.session_id).set({
                "logout_time": time.time(),
                "total_session_time_minutes": total_time_minutes
            }, merge=True)
            
            print(f"Session ended for {user_email}, total time: {total_time_minutes} minutes")
            
            self.current_page = ""
            self.page_start_time = 0
            self.login_time = 0
            self.session_id = ""
            self.current_user = ""
            
        except Exception as e:
            print(f"Error ending session: {e}")

class AdminLoginState(rx.State):
    email: str = ""
    password: str = ""
    message: str = ""
    is_authenticated: bool = False

    def set_email(self, email: str):
        self.email = email

    def set_password(self, password: str):
        self.password = password

    def login(self):
        if not (self.email and self.password):
            self.message = "All fields are required!"
            return
        user = db.collection("admin").document(self.email).get()
        if user.exists:
            hashed_password = hashlib.sha256(self.password.encode()).hexdigest()
            if user.to_dict().get("password") == hashed_password:
                self.is_authenticated = True
                self.message = "Login successful"
                # Load analytics data
                AnalyticsDashboardState.load_analytics()
            else:
                self.message = "Invalid password"
        else:
            self.message = "No admin found with this email"

class AnalyticsDashboardState(rx.State):
    all_analytics_data: list = []
    filtered_analytics_data: list = []
    session_summaries: list = []
    filter_user: str = ""
    filter_page: str = ""
    total_sessions: int = 0
    total_users: int = 0
    avg_session_time: float = 0
    most_visited_page: str = ""
    last_updated: str = ""
    auto_refresh_enabled: bool = False
    refresh_interval: int = 5
    total_data_count: int = 0

    page_visits_data: list = []
    user_sessions_data: list = []
    time_spent_data: list = []

    def set_filter_user(self, user: str):
        self.filter_user = user

    def set_filter_page(self, page: str):
        self.filter_page = page

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off and manage JS interval"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        print(f"Auto-refresh: {'ON' if self.auto_refresh_enabled else 'OFF'}")
        
        if self.auto_refresh_enabled:
            return rx.call_script(f"""
                // Stop any existing interval
                if (window.analyticsInterval) {{
                    clearInterval(window.analyticsInterval);
                }}
                
                console.log('🔄 Starting auto-refresh every {self.refresh_interval} seconds');
                
                window.analyticsInterval = setInterval(() => {{
                    console.log('🔄 Auto-refreshing analytics data...');
                    
                    // Find the manual refresh button by ID
                    const refreshBtn = document.getElementById('manual-refresh-btn');
                    if (refreshBtn) {{
                        refreshBtn.click();
                        console.log('✅ Triggered refresh via button click');
                    }} else {{
                        console.log('❌ Manual refresh button not found');
                        // Try to find any button with "Manual Refresh" text as fallback
                        const buttons = document.querySelectorAll('button');
                        for (let btn of buttons) {{
                            if (btn.textContent && btn.textContent.includes('Manual Refresh')) {{
                                btn.click();
                                console.log('✅ Triggered refresh via text search');
                                break;
                            }}
                        }}
                    }}
                }}, {self.refresh_interval * 1000});
            """)
        else:
            return rx.call_script("""
                // Stop auto-refresh
                if (window.analyticsInterval) {
                    clearInterval(window.analyticsInterval);
                    window.analyticsInterval = null;
                    console.log('🛑 Auto-refresh stopped');
                }
            """)

    def set_refresh_interval(self, interval: str):
        """Set refresh interval in seconds"""
        try:
            self.refresh_interval = max(1, int(interval))
            print(f"Refresh interval set to {self.refresh_interval} seconds")
            # If auto-refresh is enabled, restart with new interval
            if self.auto_refresh_enabled:
                return rx.call_script(f"""
                    // Restart with new interval
                    if (window.analyticsInterval) {{
                        clearInterval(window.analyticsInterval);
                    }}
                    
                    console.log('🔄 Restarting auto-refresh with new interval: {self.refresh_interval} seconds');
                    
                    window.analyticsInterval = setInterval(() => {{
                        console.log('🔄 Auto-refreshing analytics data...');
                        
                        const refreshBtn = document.getElementById('manual-refresh-btn');
                        if (refreshBtn) {{
                            refreshBtn.click();
                            console.log('✅ Triggered refresh via button click');
                        }}
                    }}, {self.refresh_interval * 1000});
                """)
        except:
            self.refresh_interval = 5

    def _extract_pages_data(self, raw_data):
        """Extract pages data from Firebase document - IMPROVED VERSION"""
        pages_data = {}
        
        # Look for any keys that start with 'pages.'
        for key, value in raw_data.items():
            if key.startswith('pages.'):
                # Parse the nested key structure: pages.pagename.property
                parts = key.split('.')
                if len(parts) >= 3:
                    page_name = parts[1]
                    property_name = parts[2]
                    
                    # Initialize page if it doesn't exist
                    if page_name not in pages_data:
                        pages_data[page_name] = {}
                    
                    # Set the property
                    pages_data[page_name][property_name] = value
                    
        print(f"🔍 Extracted pages data: {pages_data}")
        return pages_data
    
    def load_analytics(self):
        """Load all analytics data from Firebase - IMPROVED VERSION"""
        try:
            print("🔍 Loading analytics data...")
            docs = db.collection("analytics").get()
            data = []
            
            for doc in docs:
                raw_session_data = doc.to_dict()
                print(f"📋 Processing session: {doc.id}")
                print(f"📊 Raw session data keys: {list(raw_session_data.keys())}")
                
                pages_data = self._extract_pages_data(raw_session_data)
                print(f"📄 Extracted pages data: {pages_data}")
                
                total_session_time = raw_session_data.get("total_session_time_minutes", raw_session_data.get("total_session_time", 0))
                
                if total_session_time == 0 and pages_data:
                    total_from_pages = 0
                    for page_name, page_info in pages_data.items():
                        if isinstance(page_info, dict):
                            page_time = page_info.get('time_spent_minutes', page_info.get('time_spent', 0))
                            if isinstance(page_time, (int, float)):
                                total_from_pages += page_time
                    total_session_time = round(total_from_pages, 2)
                    print(f"📊 Calculated total session time from pages: {total_session_time} min")
                
                session_info = {
                    "session_id": doc.id,
                    "user_email": raw_session_data.get("user_email", "Unknown"),
                    "login_time": self._format_timestamp(raw_session_data.get("login_time", 0)),
                    "total_session_time": total_session_time,
                    "pages": pages_data  
                }
                
                print(f"✅ Processed session info with {len(pages_data)} pages")
                data.append(session_info)
            
            self.all_analytics_data = data
            self.total_data_count = len(data)
            print(f"📊 Total sessions loaded: {self.total_data_count}")
            
            self._apply_filters()
            self._prepare_chart_data()  
            self.last_updated = datetime.now().strftime("%H:%M:%S")
            print(f"✅ Analytics loaded successfully at {self.last_updated}")
            
        except Exception as e:
            print(f"❌ Error loading analytics: {e}")
            import traceback
            traceback.print_exc()
            self.all_analytics_data = []
            self.filtered_analytics_data = []
            self.session_summaries = []
            self.total_data_count = 0

    def _prepare_chart_data(self):
        """✅ NEW: Prepare data for charts"""
        try:
            print("📊 Preparing chart data...")
            
            page_visits = {}
            total_time_by_page = {}
            sessions_by_user = {}
            
            for session in self.filtered_analytics_data:
                user_email = session.get("user_email", "Unknown")
                
                # Count sessions by user
                sessions_by_user[user_email] = sessions_by_user.get(user_email, 0) + 1
                
                for page_name, page_data in session.get("pages", {}).items():
                    if isinstance(page_data, dict):
                        visits = page_data.get("visits", 0)
                        time_spent = page_data.get("time_spent_minutes", 0)
                        
                        page_visits[page_name] = page_visits.get(page_name, 0) + visits
                        total_time_by_page[page_name] = total_time_by_page.get(page_name, 0) + time_spent
            
            self.page_visits_data = [
                {"name": page, "value": visits, "fill": self._get_color(i)}
                for i, (page, visits) in enumerate(page_visits.items())
            ]
            
            sorted_users = sorted(sessions_by_user.items(), key=lambda x: x[1], reverse=True)[:10]
            self.user_sessions_data = [
                {"name": user.split('@')[0] if '@' in user else user, "value": sessions, "fill": self._get_color(i)}
                for i, (user, sessions) in enumerate(sorted_users)
            ]
            
            self.time_spent_data = [
                {"page": page, "time": round(time, 2), "fill": self._get_color(i)}
                for i, (page, time) in enumerate(total_time_by_page.items())
            ]
            
            print(f"📊 Chart data prepared:")
            print(f"   Page visits: {len(self.page_visits_data)} items")
            print(f"   User sessions: {len(self.user_sessions_data)} items")
            print(f"   Time spent: {len(self.time_spent_data)} items")
            
        except Exception as e:
            print(f"❌ Error preparing chart data: {e}")
            self.page_visits_data = []
            self.user_sessions_data = []
            self.time_spent_data = []
    
    def _get_color(self, index):
        """Get color for chart items"""
        colors = [
            "#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
            "#1abc9c", "#34495e", "#e67e22", "#95a5a6", "#16a085",
            "#27ae60", "#2980b9", "#8e44ad", "#f1c40f", "#e74c3c"
        ]
        return colors[index % len(colors)]

    def _apply_filters(self):
        """Apply filters to the data - IMPROVED VERSION WITH BETTER FORMATTING"""
        filtered_data = []
        summaries = []
        
        print(f"🔍 Applying filters to {len(self.all_analytics_data)} sessions...")
        
        for session in self.all_analytics_data:
            session_data = session
            
            # Check user filter
            user_matches = True
            if self.filter_user and self.filter_user.strip():
                user_email = session_data.get("user_email", "").lower()
                filter_user = self.filter_user.lower()
                user_matches = filter_user in user_email
                print(f"🔍 User filter: '{self.filter_user}' vs '{session_data.get('user_email')}' = {user_matches}")
            
            # Check page filter
            page_matches = True
            if self.filter_page and self.filter_page.strip():
                pages_in_session = session_data.get("pages", {}).keys()
                filter_page = self.filter_page.lower()
                page_matches = any(filter_page in page.lower() for page in pages_in_session)
                print(f"🔍 Page filter: '{self.filter_page}' in {list(pages_in_session)} = {page_matches}")
            
            # Include session if both filters match
            if user_matches and page_matches:
                filtered_data.append(session_data)
                
                pages_data = session_data.get("pages", {})
                
                print(f"📄 Processing pages for session {session_data.get('session_id', 'unknown')}")
                print(f"📄 Pages data: {pages_data}")
                print(f"📄 Pages count: {len(pages_data)}")
                
                if pages_data and len(pages_data) > 0:
                    page_info_blocks = []
                    total_pages_visited = len(pages_data)
                    total_visits = sum(page_data.get('visits', 0) for page_data in pages_data.values() if isinstance(page_data, dict))
                    
                    # Sort pages by entry time for chronological order
                    sorted_pages = sorted(
                        pages_data.items(),
                        key=lambda x: x[1].get('entry_time', 0) if isinstance(x[1], dict) else 0
                    )
                    
                    for page_name, page_data in sorted_pages:
                        print(f"🔹 Processing page: '{page_name}' with data: {page_data}")
                        
                        if isinstance(page_data, dict):
                            time_spent = page_data.get('time_spent_minutes', page_data.get('time_spent', 0))
                            visits = page_data.get('visits', 0)
                            entry_time = page_data.get('entry_time', 0)
                            exit_time = page_data.get('exit_time', 0)
                            
                            # Format timestamps
                            entry_str = self._format_timestamp(entry_time) if entry_time else "N/A"
                            exit_str = self._format_timestamp(exit_time) if exit_time else "N/A"
                            
                            # Create formatted page block
                            if self.filter_page and self.filter_page.lower() in page_name.lower():
                                page_block = f"   🎯 {page_name.upper()} (FILTERED):\n      ⏱️ Time: {time_spent} min | 👆 Visits: {visits}\n      📅 Entry: {entry_str}\n      📅 Exit: {exit_str}"
                            else:
                                page_block = f"   📄 {page_name.capitalize()}:\n      ⏱️ Time: {time_spent} min | 👆 Visits: {visits}\n      📅 Entry: {entry_str}\n      📅 Exit: {exit_str}"
                            

                            page_info_blocks.append(page_block)
                            print(f"   ✅ Added page block for {page_name}")
                    
                    pages_summary = f"\n📊 Summary: {total_pages_visited} pages, {total_visits} total visits\n" + "\n".join(page_info_blocks)
                    
                else:
                    pages_summary = "\n❌ No page data available"
                    print(f"❌ No valid pages data found for session {session_data.get('session_id', 'unknown')}")
                
                summary = f"""👤 USER: {session_data.get('user_email', 'N/A')}
🕐 LOGIN: {session_data.get('login_time', 'N/A')}
⏱️ TOTAL SESSION TIME: {session_data.get('total_session_time', 0)} minutes
🔗 SESSION ID: {session_data.get('session_id', 'N/A')}

📋 PAGE ACTIVITY:{pages_summary}
""".strip()
                
                summaries.append(summary)
                print(f"✅ Created enhanced summary for session {session_data.get('session_id', 'unknown')}")
        
        self.filtered_analytics_data = filtered_data
        self.session_summaries = summaries
        self._calculate_summary_stats()
        
        print(f"📊 Filter results: {len(filtered_data)} sessions from {len(self.all_analytics_data)} total")

    def _format_timestamp(self, timestamp):
        """Convert timestamp to readable format"""
        if timestamp:
            try:
                return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            except:
                return "Invalid time"
        return "N/A"
    
    def _calculate_summary_stats(self):
        """Calculate summary statistics based on filtered data"""
        if not self.filtered_analytics_data:
            self.total_sessions = 0
            self.total_users = 0
            self.avg_session_time = 0
            self.most_visited_page = "None"
            return
            
        self.total_sessions = len(self.filtered_analytics_data)
        unique_users = set(session.get("user_email", "") for session in self.filtered_analytics_data)
        self.total_users = len(unique_users)
        
        # Calculate average session time from filtered data
        total_time = sum(session.get("total_session_time", 0) for session in self.filtered_analytics_data if isinstance(session.get("total_session_time"), (int, float)))
        self.avg_session_time = round(total_time / self.total_sessions, 2) if self.total_sessions > 0 else 0
        
        # Find most visited page from filtered data
        page_visits = {}
        for session in self.filtered_analytics_data:
            for page_name, page_data in session.get("pages", {}).items():
                if isinstance(page_data, dict):
                    page_visits[page_name] = page_visits.get(page_name, 0) + page_data.get("visits", 0)
        
        if page_visits:
            self.most_visited_page = max(page_visits, key=page_visits.get)
        else:
            self.most_visited_page = "None"
    
    def apply_filters(self):
        """Apply user and page filters"""
        print(f"🔍 Applying filters - User: '{self.filter_user}', Page: '{self.filter_page}'")
        self._apply_filters()
        self._prepare_chart_data()  
    
    def clear_filters(self):
        """Clear all filters"""
        self.filter_user = ""
        self.filter_page = ""
        print("🧹 Filters cleared")
        self._apply_filters()
        self._prepare_chart_data()  

def analyticalpage():
    return rx.cond(
        AdminLoginState.is_authenticated,
        rx.vstack(
            # Header with real-time indicator
            rx.hstack(
                rx.heading("📊 Website Analytics Dashboard", size="8", color="#2c3e50"),
                rx.cond(
                    AnalyticsDashboardState.auto_refresh_enabled,
                    rx.badge("🔴 LIVE", color_scheme="green", font_size="sm"),
                    rx.badge("⚫ STATIC", color_scheme="gray", font_size="sm")
                ),
                rx.text(f"Last updated: {AnalyticsDashboardState.last_updated}", font_size="sm", color="gray"),
                justify="between",
                align="center",
                width="100%"
            ),
            rx.divider(),
            
            # Real-time controls with working auto-refresh
            rx.hstack(
                rx.cond(
                    AnalyticsDashboardState.auto_refresh_enabled,
                    rx.button(
                        "⏸️ Disable Auto-Refresh",
                        on_click=AnalyticsDashboardState.toggle_auto_refresh,
                        bg="#e74c3c",
                        color="white",
                        size="2"
                    ),
                    rx.button(
                        "🔄 Enable Auto-Refresh",
                        on_click=AnalyticsDashboardState.toggle_auto_refresh,
                        bg="#27ae60",
                        color="white",
                        size="2"
                    )
                ),
                rx.text("Refresh every:", font_size="sm"),
                rx.input(
                    placeholder="5",
                    value=AnalyticsDashboardState.refresh_interval,
                    on_change=AnalyticsDashboardState.set_refresh_interval,
                    width="60px",
                    type_="number"
                ),
                rx.text("seconds", font_size="sm"),
                rx.button(
                    "🔄 Manual Refresh",
                    on_click=AnalyticsDashboardState.load_analytics,
                    bg="#3498db",
                    color="white",
                    id="manual-refresh-btn",
                    size="2"
                ),
                rx.cond(
                    AnalyticsDashboardState.auto_refresh_enabled,
                    rx.text("🔄 Auto-refresh active", color="green", font_size="sm"),
                    rx.text("⏸️ Auto-refresh inactive", color="gray", font_size="sm")
                ),
                spacing="3",
                justify="center",
                align="center"
            ),
            
            rx.hstack(
                rx.box(
                    rx.vstack(
                        rx.text("📊 Filtered Sessions", font_weight="bold", color="#34495e", font_size="sm"),
                        rx.text(AnalyticsDashboardState.total_sessions, font_size="2xl", color="#3498db", font_weight="bold"),
                        rx.text(f"of {AnalyticsDashboardState.total_data_count} total", font_size="xs", color="#7f8c8d"),
                        align="center",
                        spacing="1"
                    ),
                    bg="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    padding="15px",
                    border_radius="12px",
                    width="180px",
                    border="2px solid #dee2e6",
                    _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.1)"}
                ),
                rx.box(
                    rx.vstack(
                        rx.text("👥 Unique Users", font_weight="bold", color="#34495e", font_size="sm"),
                        rx.text(AnalyticsDashboardState.total_users, font_size="2xl", color="#e74c3c", font_weight="bold"),
                        rx.text("distinct users", font_size="xs", color="#7f8c8d"),
                        align="center",
                        spacing="1"
                    ),
                    bg="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    padding="15px",
                    border_radius="12px",
                    width="180px",
                    border="2px solid #dee2e6",
                    _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.1)"}
                ),
                rx.box(
                    rx.vstack(
                        rx.text("⏱️ Avg Session", font_weight="bold", color="#34495e", font_size="sm"),
                        rx.text(f"{AnalyticsDashboardState.avg_session_time}", font_size="2xl", color="#27ae60", font_weight="bold"),
                        rx.text("minutes", font_size="xs", color="#7f8c8d"),
                        align="center",
                        spacing="1"
                    ),
                    bg="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    padding="15px",
                    border_radius="12px",
                    width="180px",
                    border="2px solid #dee2e6",
                    _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.1)"}
                ),
                rx.box(
                    rx.vstack(
                        rx.text("🔥 Top Page", font_weight="bold", color="#34495e", font_size="sm"),
                        rx.text(AnalyticsDashboardState.most_visited_page, font_size="xl", color="#f39c12", font_weight="bold"),
                        rx.text("most visited", font_size="xs", color="#7f8c8d"),
                        align="center",
                        spacing="1"
                    ),
                    bg="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                    padding="15px",
                    border_radius="12px",
                    width="180px",
                    border="2px solid #dee2e6",
                    _hover={"transform": "translateY(-2px)", "box_shadow": "0 4px 12px rgba(0,0,0,0.1)"}
                ),
                spacing="4",
                justify="center"
            ),

            rx.box(
                rx.vstack(
                    rx.heading("📈 Analytics Charts", size="6", color="#2c3e50"),
                    
                    # Charts Row 1: Two Pie Charts
                    rx.hstack(
                        # Page Visits Pie Chart
                        rx.box(
                            rx.vstack(
                                rx.heading("🔥 Page Visits Distribution", size="4", color="#34495e"),
                                rx.cond(
                                    AnalyticsDashboardState.page_visits_data,
                                    rx.recharts.pie_chart(
                                        rx.recharts.pie(
                                            data=AnalyticsDashboardState.page_visits_data,
                                            data_key="value",
                                            name_key="name",
                                            cx="50%",
                                            cy="50%",
                                            fill="#8884d8",
                                            label=True
                                        ),
                                        rx.recharts.tooltip(),
                                        width="100%",
                                        height=300
                                    ),
                                    rx.text("No page data available", color="#7f8c8d", text_align="center")
                                ),
                                align="center",
                                spacing="3"
                            ),
                            bg="white",
                            padding="20px",
                            border_radius="15px",
                            border="2px solid #e9ecef",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            width="48%"
                        ),
                        
                        # User Sessions Pie Chart
                        rx.box(
                            rx.vstack(
                                rx.heading("👥 User Sessions Distribution", size="4", color="#34495e"),
                                rx.cond(
                                    AnalyticsDashboardState.user_sessions_data,
                                    rx.recharts.pie_chart(
                                        rx.recharts.pie(
                                            data=AnalyticsDashboardState.user_sessions_data,
                                            data_key="value",
                                            name_key="name",
                                            cx="50%",
                                            cy="50%",
                                            fill="#82ca9d",
                                            label=True
                                        ),
                                        rx.recharts.tooltip(),
                                        width="100%",
                                        height=300
                                    ),
                                    rx.text("No user data available", color="#7f8c8d", text_align="center")
                                ),
                                align="center",
                                spacing="3"
                            ),
                            bg="white",
                            padding="20px",
                            border_radius="15px",
                            border="2px solid #e9ecef",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            width="48%"
                        ),
                        spacing="4",
                        justify="between",
                        width="100%"
                    ),
                    
                    # Charts Row 2: Bar Chart
                    rx.box(
                        rx.vstack(
                            rx.heading("⏱️ Time Spent by Page", size="4", color="#34495e"),
                            rx.cond(
                                AnalyticsDashboardState.time_spent_data,
                                rx.recharts.bar_chart(
                                    rx.recharts.bar(
                                        data_key="time",
                                        stroke="#8884d8",
                                        fill="#8884d8"
                                    ),
                                    rx.recharts.x_axis(data_key="page"),
                                    rx.recharts.y_axis(),
                                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                                    rx.recharts.tooltip(),
                                    data=AnalyticsDashboardState.time_spent_data,
                                    width="100%",
                                    height=400
                                ),
                                rx.text("No time data available", color="#7f8c8d", text_align="center")
                            ),
                            align="center",
                            spacing="3"
                        ),
                        bg="white",
                        padding="20px",
                        border_radius="15px",
                        border="2px solid #e9ecef",
                        box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                        width="100%",
                        margin_top="20px"
                    ),
                    
                    align="center",
                    spacing="4"
                ),
                bg="linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
                padding="25px",
                border_radius="15px",
                width="100%",
                border="2px solid #dee2e6"
            ),
            
            # Filters Section
            rx.box(
                rx.vstack(
                    rx.heading("🔍 Filters", size="5", color="#2c3e50"),
                    rx.hstack(
                        rx.vstack(
                            rx.text("👤 Filter by User:", font_weight="bold", font_size="sm", color="#34495e"),
                            rx.input(
                                placeholder="Enter user email (e.g., john@email.com)",
                                value=AnalyticsDashboardState.filter_user,
                                on_change=AnalyticsDashboardState.set_filter_user,
                                width="320px"
                            ),
                            align="start"
                        ),
                        rx.vstack(
                            rx.text("📄 Filter by Page:", font_weight="bold", font_size="sm", color="#34495e"),
                            rx.input(
                                placeholder="Enter page name (e.g., home, shop)",
                                value=AnalyticsDashboardState.filter_page,
                                on_change=AnalyticsDashboardState.set_filter_page,
                                width="320px"
                            ),
                            align="start"
                        ),
                        spacing="6"
                    ),
                    rx.hstack(
                        rx.button("🔍 Apply Filters", on_click=AnalyticsDashboardState.apply_filters, bg="#3498db", color="white", size="2"),
                        rx.button("🧹 Clear Filters", on_click=AnalyticsDashboardState.clear_filters, bg="#e74c3c", color="white", size="2"),
                        spacing="3"
                    ),
                    align="center",
                    spacing="4"
                ),
                bg="linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)",
                padding="25px",
                border_radius="15px",
                width="100%",
                border="2px solid #e9ecef",
                box_shadow="0 2px 8px rgba(0,0,0,0.1)"
            ),
            
            # Session Details
            rx.vstack(
                rx.heading("📋 Session Details", size="6", color="#2c3e50"),
                rx.cond(
                    AnalyticsDashboardState.filter_user | AnalyticsDashboardState.filter_page,
                    rx.text(f"🔍 Filtered results: User='{AnalyticsDashboardState.filter_user}' Page='{AnalyticsDashboardState.filter_page}'", 
                           color="#3498db", font_size="sm", font_weight="bold"),
                    rx.text("📊 Showing all sessions", color="#7f8c8d", font_size="sm")
                ),
                spacing="2"
            ),
            rx.divider(),
            
            # Session display
            rx.vstack(
                rx.cond(
                    AnalyticsDashboardState.session_summaries,
                    rx.foreach(
                        AnalyticsDashboardState.session_summaries,
                        lambda summary: rx.box(
                            rx.text(
                                summary, 
                                font_size="sm", 
                                white_space="pre-line",
                                font_family="'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
                                line_height="1.6"
                            ),
                            bg="linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)",
                            padding="25px",
                            border_radius="15px",
                            margin_bottom="20px",
                            border="2px solid #e9ecef",
                            box_shadow="0 4px 12px rgba(0,0,0,0.1)",
                            _hover={"transform": "translateY(-2px)", "box_shadow": "0 8px 20px rgba(0,0,0,0.15)", "border": "2px solid #3498db"},
                            width="100%",
                            transition="all 0.3s ease"
                        )
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("🔍", font_size="4xl", opacity="0.3"),
                            rx.text("No sessions match your filters", font_size="lg", color="#7f8c8d", font_weight="bold"),
                            rx.text("Try adjusting the filter criteria above", font_size="sm", color="#95a5a6"),
                            align="center",
                            spacing="2"
                        ),
                        padding="40px",
                        align="center"
                    )
                ),
                align="start",
                width="100%",
                spacing="3"
            ),
            
            spacing="8",
            align="center",
            padding="30px",
            width="100%",
            bg="linear-gradient(135deg, #f1f2f6 0%, #dfe4ea 100%)",
            min_height="100vh"
        ),
        
        # Login Form
        rx.vstack(
            rx.box(
                rx.vstack(
                    rx.text("🔐", font_size="4xl"),
                    rx.heading("Admin Login", size="8", color="#2c3e50"),
                    rx.text("Access the analytics dashboard", color="#7f8c8d"),
                    rx.input(
                        placeholder="Enter admin email",
                        value=AdminLoginState.email,
                        on_change=AdminLoginState.set_email,
                        width="320px"
                    ),
                    rx.input(
                        placeholder="Enter password",
                        type_="password",
                        value=AdminLoginState.password,
                        on_change=AdminLoginState.set_password,
                        width="320px"
                    ),
                    rx.button("🚀 Login", on_click=AdminLoginState.login, bg="#3498db", color="white", width="320px", size="3"),
                    rx.text(AdminLoginState.message, color="#e74c3c", font_weight="bold"),
                    spacing="4",
                    align="center"
                ),
                bg="white",
                padding="40px",
                border_radius="20px",
                box_shadow="0 10px 30px rgba(0,0,0,0.1)",
                border="2px solid #e9ecef"
            ),
            justify="center",
            align="center",
            min_height="100vh",
            bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        )
    )