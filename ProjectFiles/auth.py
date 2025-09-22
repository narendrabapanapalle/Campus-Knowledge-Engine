import streamlit as st
import hashlib
import os
from database import DatabaseManager
from PIL import Image
import base64
from io import BytesIO

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.create_tables()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def set_auth_page_styling(self):
        """Set styling for the authentication page to match the reference design"""
        style = """
        <style>
        /* Main app background - Dark theme to match the reference */
        .stApp {
            background: orange;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        /* Hide header */
        [data-testid="stHeader"] {
            display: none;
        }
        
        /* Main container styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Title styling */
        .main-title {
            color: white;
            text-align: center;
            font-size: 3.2rem;
            font-weight: bold;
            margin-bottom: 3rem;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.1);
        }
        
        /* Auth form container */
        .auth-form-container {
            background: rgba(30, 30, 30, 0.95);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        
        /* Remove unwanted spacing */
        .stButton {
            margin-bottom: 0 !important;
        }
        
        .block-container > div {
            gap: 0 !important;
        }
        
        .element-container {
            margin-bottom: 0 !important;
        }
        
        /* Tab buttons styling */
        .auth-tabs {
            display: flex;
            margin-bottom: 2rem;
            border-radius: 8px;
            overflow: hidden;
            background: rgba(50, 50, 50, 0.5);
        }
        
        .auth-tabs button {
            flex: 1;
            padding: 12px 20px;
            background: rgba(70, 70, 70, 0.8);
            color: red;
            border: none;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .auth-tabs button:hover {
            background: rgba(90, 90, 90, 0.9);
        }
        
        .auth-tabs button.active {
            background: #007bff;
            color: red;
        }
        
        /* Form input styling */
        .stTextInput > div > div > input {
            background: rgba(50, 50, 50, 0.9) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 14px !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #007bff !important;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25) !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.6) !important;
        }
        
        .stTextInput label {
            color: white !important;
            font-weight: 500 !important;
            margin-bottom: 8px !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: #007bff !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            width: 100% !important;
            transition: background-color 0.3s ease !important;
        }
        
        .stButton > button:hover {
            background: #0056b3 !important;
        }
        
        /* Form submit button special styling */
        .login-submit-btn > button {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 14px 24px !important;
            font-weight: 600 !important;
            font-size: 16px !important;
            width: 100% !important;
            margin-top: 1rem !important;
            box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3) !important;
        }
        
        /* Checkbox styling */
        .stCheckbox label {
            color: white !important;
        }
        
        /* File uploader styling */
        .stFileUploader > div {
            background: rgba(50, 50, 50, 0.9) !important;
            border: 1px dashed rgba(255, 255, 255, 0.3) !important;
            border-radius: 8px !important;
        }
        
        .stFileUploader label {
            color: white !important;
        }
        
        /* Legal image container */
        .legal-image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            padding: 2rem;
        }
        
        /* Link styling */
        a {
            color: #87ceeb !important;
            text-decoration: none !important;
        }
        
        a:hover {
            color: #add8e6 !important;
        }
        
        /* Additional spacing and layout */
        .form-section {
            margin-bottom: 1.5rem;
        }
        
        .forgot-password {
            text-align: right;
            margin-top: 0.5rem;
        }
        
        .forgot-password a {
            color: #87ceeb;
            font-size: 14px;
        }
        
        /* Success/Error message styling */
        .stAlert {
            background: rgba(40, 40, 40, 0.9) !important;
            color: white !important;
            border-radius: 8px !important;
        }
        </style>
        """
        st.markdown(style, unsafe_allow_html=True)
    
    def show_auth_page(self):
        """Display the main authentication page matching the reference design"""
        st.set_page_config(
            page_title="Campus Knowledge Engine- Login",
            page_icon="",
            layout="wide"
        )
        
        # Apply custom styling
        self.set_auth_page_styling()
        
        # Main title
        st.markdown("""
            <div class="main-title">
                Campus Knowledge Engine
            </div>
        """, unsafe_allow_html=True)
        
        # Create main layout - image on left, form on right
        col_img, col_form = st.columns([1, 1], gap="large")
        
        # Left column - Legal image
        with col_img:
            st.markdown('<div class="legal-image-container">', unsafe_allow_html=True)
            
            # Try to load the college_logo.jpg
            if os.path.exists("college_logo.jpg"):
                try:
                # --- CHANGE: Using HTML to control both width and height ---
                    import base64
                    with open("college_logo.jpg", "rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode()
                    
                    st.markdown(f"""
                        <img src="data:image/jpeg;base64,{img_data}" 
                            style="width: 776px; height: 450px; object-fit: cover; border-radius: 15px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);" 
                            alt="Legal System">
                    """, unsafe_allow_html=True)
                except:
                    # Fallback if image can't be loaded
                    st.markdown("""
                        <div style="
                            width: 500px; 
                            height: 400px; 
                            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                            border-radius: 15px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            border: 2px dashed rgba(255,255,255,0.3);
                        ">
                            <div style="text-align: center; color: white;">
                                <h3>College System</h3>
                                <p>Place your college_logo.jpg here</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # Show placeholder if image not found
                st.markdown("""
                    <div style="
                        width: 500px; 
                        height: 400px; 
                        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); 
                        border-radius: 15px; 
                        display: flex; 
                        align-items: center; 
                        justify-content: center; 
                        border: 2px dashed rgba(255,255,255,0.3);
                    ">
                        <div style="text-align: center; color: white;">
                            <h3> college System</h3>
                            <p>Place your college_logo.jpg here</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Right column - Authentication form
        with col_form:
            # Tab selection
            if 'auth_tab' not in st.session_state:
                st.session_state.auth_tab = 'login'

            # Show appropriate form based on selected tab
            if st.session_state.auth_tab == 'login':
                self.show_login_form()
            else:
                self.show_register_form()

    def show_login_form(self):
        """Display the login form"""
        st.markdown("### 🔐 Sign In to Your Account")

        # Create tab buttons with no spacing
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("LOGIN", key="login_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'login'
                st.rerun() 
        with tab_col2:
            if st.button("REGISTER", key="register_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'register'
                st.rerun()

        # Add some vertical space
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            # Email input
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            email = st.text_input(
                "Email address",
                placeholder="example@gmail.com",
                key="login_email"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Password input
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Login button
            st.markdown('<div class="login-submit-btn">', unsafe_allow_html=True)
            login_submitted = st.form_submit_button("Sign in")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle login submission
            if login_submitted:
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    # Authenticate user
                    user_data = self.authenticate_user(email, password)
                    if user_data:
                        user_id, first_name, last_name, email_db = user_data
                        
                        # Set session state
                        st.session_state.user_id = user_id
                        st.session_state.user_name = f"{first_name} {last_name}"
                        st.session_state.user_email = email_db
                        
                        # Always use a single session per user
                        session_id = f"user_{user_id}_main_session"
                        st.session_state.session_id = session_id
                        
                        # Ensure session exists in database
                        self.db.create_user_session(user_id, session_id, "Main Chat")
                        
                        st.success(f"Welcome back, {first_name} {last_name}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password")
    
    def show_register_form(self):
        """Display the registration form"""
        st.markdown("### 📝 Create New Account")

        # Create tab buttons with no spacing
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("LOGIN", key="login_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'login'
                st.rerun()
        with tab_col2:
            if st.button("REGISTER", key="register_tab_btn", use_container_width=True):
                st.session_state.auth_tab = 'register'
                st.rerun()

        # Add some vertical space
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        with st.form("register_form", clear_on_submit=True):
            # Name inputs
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name", key="reg_first_name")
            with col2:
                last_name = st.text_input("Last Name", key="reg_last_name")
            
            # Email input
            email = st.text_input(
                "Email address",
                placeholder="Enter your email address",
                key="reg_email"
            )
            
            # Password inputs
            col3, col4 = st.columns(2)
            with col3:
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="reg_password"
                )
            with col4:
                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Confirm your password",
                    key="reg_confirm_password"
                )
            
            # Profile picture upload
            st.markdown("**Profile Picture (Optional)**")
            uploaded_file = st.file_uploader(
                "Choose a profile picture",
                type=['png', 'jpg', 'jpeg'],
                help="Limit 200MB per file • PNG, JPG, JPEG",
                key="reg_profile_picture"
            )
            
            # Register button
            st.markdown('<div class="login-submit-btn">', unsafe_allow_html=True)
            register_submitted = st.form_submit_button("Create Account")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Handle registration submission
            if register_submitted:
                # Validation
                if not all([first_name, last_name, email, password, confirm_password]):
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif self.db.user_exists(email):
                    st.error("An account with this email already exists")
                else:
                    # Process profile picture
                    profile_pic_data = None
                    if uploaded_file is not None:
                        try:
                            # Convert image to base64
                            image = Image.open(uploaded_file)
                            # Resize image to reasonable size
                            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                            buffered = BytesIO()
                            image.save(buffered, format="PNG")
                            profile_pic_data = base64.b64encode(buffered.getvalue()).decode()
                        except Exception as e:
                            st.error(f"Error processing profile picture: {str(e)}")
                            return
                    
                    # Create user
                    success = self.create_user(first_name, last_name, email, password, profile_pic_data)
                    if success:
                        st.success("Account created successfully! Please login.")
                        st.session_state.auth_tab = 'login'
                        st.rerun()
                    else:
                        st.error("Failed to create account. Please try again.")
    
    def authenticate_user(self, email, password):
        """Authenticate user credentials"""
        hashed_password = self.hash_password(password)
        return self.db.verify_user(email, hashed_password)
    
    def create_user(self, first_name, last_name, email, password, profile_pic_data=None):
        """Create a new user account"""
        hashed_password = self.hash_password(password)
        return self.db.create_user(first_name, last_name, email, hashed_password, profile_pic_data)
    
    def get_user_profile_picture(self, user_id):
        """Get user's profile picture"""
        profile_pic_data = self.db.get_user_profile_picture(user_id)
        if profile_pic_data:
            try:
                # Convert base64 back to image
                image_data = base64.b64decode(profile_pic_data)
                image = Image.open(BytesIO(image_data))
                return image
            except:
                return None
        return None
    
    def show_profile_page(self, user_id):
        """Show user profile page"""
        user_info = self.db.get_user_info(user_id)
        if not user_info:
            st.error("User not found")
            return
        
        user_id, first_name, last_name, email, created_at, profile_pic_data = user_info
        
        st.title("👤 User Profile")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display profile picture
            if profile_pic_data:
                try:
                    image_data = base64.b64decode(profile_pic_data)
                    image = Image.open(BytesIO(image_data))
                    st.image(image, width=200, caption="Profile Picture")
                except:
                    self._show_default_avatar(first_name[0] if first_name else "U")
            else:
                self._show_default_avatar(first_name[0] if first_name else "U")
            
            # Upload new profile picture
            st.markdown("---")
            new_pic = st.file_uploader(
                "Update Profile Picture", 
                type=['png', 'jpg', 'jpeg'],
                key="update_profile_pic"
            )
            
            if new_pic and st.button("Update Picture"):
                try:
                    image = Image.open(new_pic)
                    image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                    buffered = BytesIO()
                    image.save(buffered, format="PNG")
                    new_pic_data = base64.b64encode(buffered.getvalue()).decode()
                    
                    if self.db.update_profile_picture(user_id, new_pic_data):
                        st.success("Profile picture updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update profile picture")
                except Exception as e:
                    st.error(f"Error updating profile picture: {str(e)}")
        
        with col2:
            st.markdown("### 📋 Profile Information")
            
            # Display user information
            st.markdown(f"**Name:** {first_name} {last_name}")
            st.markdown(f"**Email:** {email}")
            st.markdown(f"**Member Since:** {created_at}")
            
            st.markdown("---")
            
            # Profile update form
            st.markdown("### ✏️ Update Profile")
            
            with st.form("update_profile_form"):
                new_first_name = st.text_input("First Name", value=first_name)
                new_last_name = st.text_input("Last Name", value=last_name)
                new_email = st.text_input("Email", value=email)
                
                col3, col4 = st.columns(2)
                with col3:
                    new_password = st.text_input("New Password (optional)", type="password")
                with col4:
                    confirm_new_password = st.text_input("Confirm New Password", type="password")
                
                update_button = st.form_submit_button("Update Profile", type="primary")
                
                if update_button:
                    # Validate inputs
                    if not all([new_first_name, new_last_name, new_email]):
                        st.error("Please fill in all required fields")
                    elif new_password and new_password != confirm_new_password:
                        st.error("New passwords do not match")
                    elif new_password and len(new_password) < 6:
                        st.error("Password must be at least 6 characters long")
                    else:
                        # Check if new email is already taken by another user
                        if new_email != email and self.db.user_exists(new_email):
                            st.error("This email is already taken by another user")
                        else:
                            # Update profile
                            hashed_new_password = self.hash_password(new_password) if new_password else None
                            success = self.db.update_user_profile(
                                user_id, new_first_name, new_last_name, 
                                new_email, hashed_new_password
                            )
                            
                            if success:
                                st.success("Profile updated successfully!")
                                # Update session state
                                st.session_state.user_name = f"{new_first_name} {new_last_name}"
                                st.rerun()
                            else:
                                st.error("Failed to update profile")
            
    
    def _show_default_avatar(self, initial):
        """Show default avatar with user's initial"""
        st.markdown(f"""
        <div style="
            width: 200px; 
            height: 200px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            color: white; 
            font-weight: bold; 
            font-size: 48px;
            margin: 0 auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">{initial}</div>
        """, unsafe_allow_html=True)
    
    def logout(self):
        """Handle user logout"""
        # Clear session state
        for key in list(st.session_state.keys()):
            if key.startswith(('user_', 'session_', 'messages', 'show_profile', 'auth_tab')):
                del st.session_state[key]
        
        st.success("Logged out successfully!")
        st.rerun()