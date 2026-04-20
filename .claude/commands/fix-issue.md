# /fix-issue — Fix a GitHub Issue Command

When user types `/fix-issue [issue description or number]`, follow this workflow:

## Step 1: Understand the issue
- Parse the issue description or number
- Ask clarifying questions if the issue is ambiguous
- Re-read CLAUDE.md to understand which system/component is affected
- Determine if it's a bug fix, feature request, or refactoring task

## Step 2: Locate affected code
- Search codebase for relevant files using Grep or Glob
- Map out the call chain: where is the bug triggered, what needs to change
- List all files that will need modifications
- Check if existing tests cover this area

## Step 3: Write a fix plan (ASK BEFORE IMPLEMENTING)
Show the user the plan:
```
I'll fix this by:
1. Modifying [file1] to [specific change]
2. Modifying [file2] to [specific change]
3. Adding test [test_name] in [file] to cover [case]
4. Updating [docs] if needed
```

**Ask**: "Proceed with this plan?" (wait for approval)

## Step 4: Implement the fix
- Implement changes following ALL rules in `.claude/rules/`
- Ensure type hints, docstrings, and error handling
- Write tests immediately after each code change
- Run tests: `pytest tests/ -v -k [relevant_test]` to verify

## Step 5: Verify and commit
- Show diff: `git diff`
- Run `/review [changed files]` to catch any rule violations
- If review passes: Create a clean commit:
  ```
  git add [specific files]
  git commit -m "fix: [issue description]"
  ```
- Update PROGRESS.md with the fix details
- Push to branch: `git push origin [feature-branch]`

## Example Usage

```
/fix-issue Scoring algorithm doesn't handle null ratings
/fix-issue #42
/fix-issue API returns 500 instead of 400 for invalid area parameter
```

---

**Last Updated**: 2026-04-20
