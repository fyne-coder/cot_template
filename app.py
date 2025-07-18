from __future__ import annotations
import streamlit as st
from typing import List, Tuple
from cot_templates import run_workflow_a, run_workflow_b

# Initialize sidebar state
st.set_page_config(page_title="COT Simulator", page_icon="⚙️", layout="wide")
with st.sidebar:
    st.header("Settings")
    model_name = st.text_input("OpenAI model", value=None, placeholder="gpt-4.1")
    step_mode = st.checkbox("Enable step-by-step reveal", value=False)

st.title("Chain-of-Thought Workflow Simulator")

# Workflow selector
workflow = st.selectbox(
    "Select workflow",
    ["Workflow A: Code Issue", "Workflow B: Requirements Template"],
)

prompt = st.text_area("Enter your prompt here", height=150)

# Roles input for Workflow B
roles: List[str] = []
if workflow == "Workflow B: Requirements Template":
    st.markdown("### Critique Roles (provide exactly three unique roles)")
    cols = st.columns(3)
    role1 = cols[0].text_input("Role 1")
    role2 = cols[1].text_input("Role 2")
    role3 = cols[2].text_input("Role 3")
    roles = [role1.strip(), role2.strip(), role3.strip()]

if st.button("Run COT"):
    # Basic validation
    if not prompt.strip():
        st.warning("Please enter a prompt.")
        st.stop()
    if workflow.startswith("Workflow B"):
        if len(set(roles)) != 3 or any(r == "" for r in roles):
            st.warning("Provide three unique, non-empty critique roles.")
            st.stop()

    # Run and catch errors
    try:
        if workflow.startswith("Workflow A"):
            result = run_workflow_a(prompt, model=model_name)
        else:
            result = run_workflow_b(prompt, roles, model=model_name)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    # Prepare messages for display
    messages: List[Tuple[str,str]] = []
    if workflow.startswith("Workflow A"):
        # Step 1: solutions
        table = "|Solution|Score|Rationale|\n|---|---|---|\n"
        for c in result["candidates"]:
            table += f"|{c['title']}|{c['score']}|{c['rationale']}|\n"
        messages.append(("assistant", "**Candidates & scores**\n\n" + table))
        messages.append(("user", "Which solution do you recommend and why?"))
        # Step 2: recommendation
        rec = (
            f"**Recommendation**: {result['recommendation']}\n\n"
            f"**Why**: {result['why']}\n\n"
            "**Next steps / acceptance criteria**:\n" + "\n".join(f"- {x}" for x in result['acceptance'])
        )
        messages.append(("assistant", rec))
    else:
        # Workflow B
        messages.append(("assistant", "**Initial template**\n\n" + result['template_initial']))
        messages.append(("user", f"Critique as: {', '.join(roles)}"))
        critique_md = "\n\n".join(f"**{role}**:\n{result['critique'][role]}"for role in roles)
        messages.append(("assistant", critique_md))
        messages.append(("user", "Improve the template based on your critique."))
        messages.append(("assistant", "**Improved template**\n\n" + result['template_improved']))

    # Step-by-step state
    if step_mode:
        if 'step' not in st.session_state:
            st.session_state.step = 0
    else:
        st.session_state.step = len(messages) - 1

    # Display messages
    for idx, (role, content) in enumerate(messages):
        if idx <= st.session_state.step:
            if role == "assistant":
                with st.chat_message("assistant"):
                    st.markdown(content, unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<div style='background:#D5E4FF; padding:8px; border-radius:5px;'>"
                    f"<strong>User:</strong> {content}</div>",
                    unsafe_allow_html=True
                )

    # Navigation buttons
    if step_mode and st.session_state.step < len(messages) - 1:
        if st.button("Next step"):
            st.session_state.step += 1
    elif step_mode and st.session_state.step == len(messages) - 1:
        if st.button("Restart steps"):
            st.session_state.step = 0