import uuid
import time

# In-memory session storage (use DB for production)
sessions = {}

class WorkflowStatus:
    """Workflow status constants"""
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

def create_session(workflow, metadata=None, user_id="demo_user"):
    """Create a new workflow session"""
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "session_id": session_id,
        "user_id": user_id,
        "workflow": workflow,
        "status": WorkflowStatus.RUNNING,
        "metadata": metadata or {},
        "required_input": [],
        "created_at": time.time(),
        "updated_at": time.time()
    }
    
    print(f"✅ Created session {session_id} for workflow: {workflow}")
    return session_id

def get_session(session_id):
    """Get session by ID"""
    return sessions.get(session_id)

def update_session(session_id, **updates):
    """Update session metadata"""
    if session_id not in sessions:
        return False
    
    session = sessions[session_id]
    
    # Update metadata
    for key, value in updates.items():
        if key == "metadata":
            session["metadata"].update(value)
        else:
            session[key] = value
    
    session["updated_at"] = time.time()
    
    print(f"✅ Updated session {session_id}: {updates}")
    return True

def set_waiting(session_id, required_input):
    """Set session to WAITING status with required input"""
    if session_id not in sessions:
        return False
    
    sessions[session_id]["status"] = WorkflowStatus.WAITING
    sessions[session_id]["required_input"] = required_input if isinstance(required_input, list) else [required_input]
    sessions[session_id]["updated_at"] = time.time()
    
    print(f"⏸️  Session {session_id} waiting for: {required_input}")
    return True

def set_completed(session_id):
    """Mark session as completed"""
    if session_id not in sessions:
        return False
    
    sessions[session_id]["status"] = WorkflowStatus.COMPLETED
    sessions[session_id]["updated_at"] = time.time()
    
    print(f"✅ Session {session_id} completed")
    return True

def delete_session(session_id):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        print(f"🗑️  Deleted session {session_id}")
        return True
    return False

def get_metadata(session_id, key=None):
    """Get metadata from session"""
    session = get_session(session_id)
    if not session:
        return None
    
    if key:
        return session["metadata"].get(key)
    return session["metadata"]

def is_ready_to_execute(session_id):
    """Check if session has all required data to execute"""
    session = get_session(session_id)
    if not session:
        return False
    
    return session["status"] == WorkflowStatus.COMPLETED or len(session["required_input"]) == 0
