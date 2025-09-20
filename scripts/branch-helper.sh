#!/bin/bash

# Script d'aide pour la gestion des branches AGI-EVE

case "$1" in
  "new-feature")
    feature_name="$2"
    git flow feature start "$feature_name"
    echo "✅ Branche feature/$feature_name créée"
    ;;
    
  "finish-feature")
    feature_name="$2"
    git flow feature finish "$feature_name"
    echo "✅ Feature $feature_name mergée"
    ;;
    
  "hotfix")
    version="$2"
    git flow hotfix start "$version"
    echo "✅ Branche hotfix/$version créée"
    ;;
    
  "release")
    version="$2"
    git flow release start "$version"
    echo "✅ Branche release/$version créée"
    ;;
    
  *)
    echo "Usage: $0 {new-feature|finish-feature|hotfix|release} [nom]"
    ;;
esac
