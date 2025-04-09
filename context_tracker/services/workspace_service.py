from ..repositories.workspace_repository import WorkspaceRepository

class WorkspaceService:
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()

    def get_user_workspaces(self, user):
        return self.workspace_repo.get_user_workspaces(user)

    def join_workspace(self, workspace_id, user):
        workspace = self.workspace_repo.get_workspace_by_id(workspace_id)
        if not workspace:
            return {'error': 'Workspace not found', 'status': 404}
        self.workspace_repo.add_member_to_workspace(workspace, user)
        return {'message': 'Joined workspace successfully'}