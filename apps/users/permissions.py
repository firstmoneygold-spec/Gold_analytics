from rest_framework.permissions import BasePermission

class IsProUser(BasePermission):
    """
    Allows access only to authenticated users with PRO or ENTERPRISE subscriptions.
    """
    message = "This advanced analytical feature requires a Pro Trader or Institutional subscription."

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_pro_or_higher
        )


class HasPredictionQuota(BasePermission):
    """
    Allows access only if the user has available daily quota or remaining credits.
    """
    message = "Prediction quota exceeded. Please upgrade to Pro Trader for unlimited predictions."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        can_predict, reason = request.user.can_make_prediction()
        if not can_predict:
            self.message = reason
        return can_predict
