import streamlit as st
import openai
import time
import re

# Set page configuration
st.set_page_config(
    page_title="AI Prompt Enhancer",
    page_icon="✨",
    layout="wide"
)

# App title and description
st.title("AI Prompt Enhancer")
st.markdown("""
    This app helps you create better prompts for AI systems by refining your initial Role, Context, and Task specifications.
    Enter your API key and initial prompt information below to get started.
""")

# OpenAI API key input
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    model_choice = st.selectbox(
        "Select OpenAI Model",
        ["gpt-4", "gpt-4o", "gpt-3.5-turbo"],
        index=2  # Default to GPT-3.5 Turbo as requested
    )
    st.markdown("---")
    st.markdown("### How to use this app")
    st.markdown("""
    1. Enter your OpenAI API key
    2. Fill in the Role, Context, and Task fields
    3. Click 'Enhance My Prompt'
    4. Review the improved prompt and feedback
    """)

# Function to call OpenAI API
def enhance_prompt(role, context, task, model):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
        return None, None
    
    try:
        # Set up OpenAI with the provided API key
        client = openai.OpenAI(api_key=api_key)
        
        # Define the system message that instructs the AI how to enhance prompts
        system_message = """
        You are an expert prompt engineer who helps improve prompts for AI systems. Your task is to analyze
        the user's provided Role, Context, and Task components and generate a more effective prompt.
        
        For each component:
        1. Identify missing information or ambiguities
        2. Suggest improvements for clarity and specificity
        3. Note any assumptions you're making
        
        Then create an enhanced version of the full prompt that combines these components effectively.
        
        IMPORTANT: Format your response exactly as follows:
        
        ## Analysis
        [Your analysis of the prompt components here]
        
        ## Enhanced Prompt
        [The complete enhanced prompt here]
        """
        
        # Prepare the user message with the Role, Context, and Task
        user_message = f"""
        Please help me enhance the following prompt components:
        
        ROLE: {role}
        
        CONTEXT: {context}
        
        TASK: {task}
        """
        
        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Extract the response content
        enhanced_prompt_full = response.choices[0].message.content
        
        # More robust parsing method
        analysis = ""
        final_prompt = ""
        
        # First, try to split by markdown headers
        if "## Analysis" in enhanced_prompt_full and "## Enhanced Prompt" in enhanced_prompt_full:
            parts = enhanced_prompt_full.split("## Enhanced Prompt")
            analysis = parts[0].replace("## Analysis", "").strip()
            final_prompt = parts[1].strip()
        
        # If that fails, try other common patterns
        elif "ENHANCED PROMPT:" in enhanced_prompt_full:
            parts = enhanced_prompt_full.split("ENHANCED PROMPT:")
            analysis = parts[0].strip()
            final_prompt = "ENHANCED PROMPT:" + parts[1].strip()
        
        # If all else fails, try to find a section that looks like a prompt
        elif "ROLE:" in enhanced_prompt_full and "TASK:" in enhanced_prompt_full:
            # Use regex to find the prompt section
            prompt_pattern = r"(ROLE:.*?TASK:.*?)(?=\n\n|$)"
            prompt_match = re.search(prompt_pattern, enhanced_prompt_full, re.DOTALL)
            
            if prompt_match:
                # Everything before the matched prompt is analysis
                match_start = prompt_match.start()
                analysis = enhanced_prompt_full[:match_start].strip()
                final_prompt = prompt_match.group(0).strip()
            else:
                # Just show everything as analysis if we couldn't identify a clear prompt
                analysis = enhanced_prompt_full
                final_prompt = "Could not identify a clear prompt section. Please see the analysis tab."
        else:
            # Just show everything as analysis if we couldn't identify a clear prompt
            analysis = enhanced_prompt_full
            final_prompt = "Could not identify a clear prompt section. Please see the analysis tab."
        
        return analysis, final_prompt
        
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return None, None

# Main form for prompt components
with st.container():
    st.header("Enter Your Prompt Components")
    
    with st.form("prompt_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.text_area("ROLE (Who should the AI be?)", 
                               placeholder="Example: You are an expert marketing consultant with 20 years of experience...",
                               height=150)
        
        with col2:
            context = st.text_area("CONTEXT (Background information)", 
                                  placeholder="Example: I'm launching a new eco-friendly product and need help with...",
                                  height=150)
        
        task = st.text_area("TASK (What should the AI do?)", 
                           placeholder="Example: Create a comprehensive marketing strategy focusing on...",
                           height=150)
        
        submit = st.form_submit_button("Enhance My Prompt")

# Process form submission
if submit:
    if not (role and context and task):
        st.warning("Please fill in all three prompt components")
    else:
        with st.spinner("Enhancing your prompt..."):
            # Add a small delay to make the spinner visible even if processing is fast
            time.sleep(0.5)
            analysis, enhanced_prompt = enhance_prompt(role, context, task, model_choice)
            
            if analysis and enhanced_prompt:
                st.success("Prompt enhanced successfully!")
                
                # Display tabs for different views
                tab1, tab2, tab3 = st.tabs(["Enhanced Prompt", "Analysis & Feedback", "Original vs Enhanced"])
                
                with tab1:
                    st.header("Enhanced Prompt")
                    st.markdown(enhanced_prompt)
                    # Ensure we're using UTF-8 encoding when saving the data
                    st.download_button(
                        label="Download Enhanced Prompt",
                        data=enhanced_prompt,
                        file_name="enhanced_prompt.txt",
                        mime="text/plain"
                    )
                
                with tab2:
                    st.header("Analysis & Feedback")
                    st.markdown(analysis)
                
                with tab3:
                    st.header("Original vs Enhanced")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Components")
                        st.markdown("**ROLE:**")
                        st.markdown(role)
                        st.markdown("**CONTEXT:**")
                        st.markdown(context)
                        st.markdown("**TASK:**")
                        st.markdown(task)
                    
                    with col2:
                        st.subheader("Enhanced Prompt")
                        st.markdown(enhanced_prompt)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and OpenAI API")