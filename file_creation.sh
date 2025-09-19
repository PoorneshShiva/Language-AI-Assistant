#!/usr/bin/env bash
set -euo pipefail

# 1. Move config into lexilearn root
# mv src/lexilearn/config.py src/lexilearn/

# 2. Prepare new GraphQL subdirectories
mkdir -p src/lexilearn/graphql/{mutations,queries,types}

# 3. Migrate mutation files and rename
mv src/lexilearn/graphql/assignments/mutations.py src/lexilearn/graphql/mutations/assignments_mutations.py
mv src/lexilearn/graphql/evaluations/mutations.py src/lexilearn/graphql/mutations/evaluations_mutations.py
mv src/lexilearn/graphql/grammar/mutations.py src/lexilearn/graphql/mutations/grammar_mutations.py
mv src/lexilearn/graphql/transcription/mutations.py src/lexilearn/graphql/mutations/transcriptions_mutations.py

# 4. Migrate query files and rename
mv src/lexilearn/graphql/assignments/queries.py src/lexilearn/graphql/queries/assignments_queries.py
mv src/lexilearn/graphql/evaluations/queries.py src/lexilearn/graphql/queries/evaluations_queries.py
mv src/lexilearn/graphql/grammar/queries.py src/lexilearn/graphql/queries/grammar_queries.py
mv src/lexilearn/graphql/transcription/queries.py src/lexilearn/graphql/queries/transcriptions_queries.py

# 5. Move type definitions (if present)
# e.g., grammar_types or other type files
# Uncomment and adapt if you have more types
# mv src/lexilearn/graphql/types/grammar_types.py src/lexilearn/graphql/types/

# 6. Clean up old GraphQL directories
rm -rf src/lexilearn/graphql/{assignments,evaluations,grammar,transcription}

# 7. Re-create __init__.py in new folders
for d in src/lexilearn/graphql/{mutations,queries,types}; do
  touch "$d/__init__.py"
done

# 8. Reorganize utils: move agent_graphs into agents/graphs
mkdir -p src/lexilearn/utils/agents/graphs
mv src/lexilearn/utils/agent_graphs/* src/lexilearn/utils/agents/graphs/
rm -rf src/lexilearn/utils/agent_graphs

# 9. Ensure __init__.py for graphs
touch src/lexilearn/utils/agents/graphs/__init__.py

# 10. (Optional) Adjust imports in codebase to reflect new paths
# You may need to update import statements in .py files accordingly.

echo "Restructure complete. Please review and run tests to validate imports."

