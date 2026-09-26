#!/usr/bin/env bash
set -euo pipefail

PROFILE="${AWS_PROFILE:-task4-lab}"
REGION="${AWS_REGION:-us-east-1}"
STACK="swe40006-task4-board"

echo "Captured: $(date -Iseconds)"
echo "AWS profile: ${PROFILE}; region: ${REGION}"
echo
echo '$ aws sts get-caller-identity (lab account only)'
aws sts get-caller-identity --profile "$PROFILE" --region "$REGION" \
  --query 'Account' --output text
echo
echo '$ aws cloudformation describe-stacks (status and public URL)'
aws cloudformation describe-stacks --stack-name "$STACK" --profile "$PROFILE" --region "$REGION" \
  --query 'Stacks[0].[StackStatus,Outputs[?OutputKey==`PublicUrl`].OutputValue|[0]]' --output text
echo
echo '$ aws ecs describe-services (desired and running tasks)'
aws ecs describe-services --cluster swe40006-task4 --services deployment-board \
  --profile "$PROFILE" --region "$REGION" \
  --query 'services[0].[status,desiredCount,runningCount,pendingCount]' --output text
echo
echo '$ aws ecs describe-task-definition (image and platform)'
aws ecs describe-task-definition --task-definition swe40006-task4-board \
  --profile "$PROFILE" --region "$REGION" \
  --query 'taskDefinition.[family,cpu,memory,requiresCompatibilities[0],containerDefinitions[0].image]' --output text
echo
TARGET_GROUP=$(aws elbv2 describe-target-groups --profile "$PROFILE" --region "$REGION" \
  --query 'TargetGroups[?contains(TargetGroupName, `swe400`)].TargetGroupArn|[0]' --output text)
echo '$ aws elbv2 describe-target-health'
aws elbv2 describe-target-health --target-group-arn "$TARGET_GROUP" \
  --profile "$PROFILE" --region "$REGION" \
  --query 'TargetHealthDescriptions[].[Target.Id,TargetHealth.State]' --output text
echo
URL=$(aws cloudformation describe-stacks --stack-name "$STACK" --profile "$PROFILE" --region "$REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`PublicUrl`].OutputValue|[0]' --output text)
echo "\$ curl -i ${URL}health"
curl -fsSi "${URL}health"
echo
echo "\$ curl -i ${URL}api/status"
curl -fsSi "${URL}api/status"
echo
echo "\$ curl -o /dev/null -w 'root HTTP %{http_code} from %{remote_ip}\\n' ${URL}"
curl -fsS -o /dev/null -w 'root HTTP %{http_code} from %{remote_ip}\n' "$URL"
