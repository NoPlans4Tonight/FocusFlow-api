from ..models import Workspace

class WorkspaceRepository:
    def create_workspace(self, name, owner):
        return Workspace.objects.create(name=name, owner=owner)

    def get_workspace_by_id(self, workspace_id):
        return Workspace.objects.filter(id=workspace_id).first()

    def add_member_to_workspace(self, workspace, user):
        workspace.members.add(user)

    def get_user_workspaces(self, user):
        return user.workspaces.all()