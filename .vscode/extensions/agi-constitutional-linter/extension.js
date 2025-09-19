const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

class AGIConstitutionalLinter {
    constructor() {
        this.diagnosticCollection = vscode.languages.createDiagnosticCollection('agi-constitutional');
        this.constitution = null;
        this.loadConstitution();
    }

    loadConstitution() {
        try {
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) return;
            
            const constitutionPath = path.join(workspaceFolder.uri.fsPath, 'iaGOD.json');
            if (fs.existsSync(constitutionPath)) {
                const constitutionContent = fs.readFileSync(constitutionPath, 'utf8');
                this.constitution = JSON.parse(constitutionContent);
                console.log('AGI Constitution loaded successfully');
            }
        } catch (error) {
            console.error('Error loading AGI Constitution:', error);
        }
    }

    lintDocument(document) {
        if (!this.constitution || document.languageId !== 'python') {
            return;
        }

        const diagnostics = [];
        const text = document.getText();
        const lines = text.split('\n');

        // Vérification limite 200 lignes
        if (lines.length > 200) {
            const diagnostic = new vscode.Diagnostic(
                new vscode.Range(199, 0, lines.length - 1, 0),
                `Fichier dépasse la limite constitutionnelle: ${lines.length} lignes (max: 200)`,
                vscode.DiagnosticSeverity.Error
            );
            diagnostic.code = 'AGI-LIMIT-001';
            diagnostic.source = 'AGI Constitutional Linter';
            diagnostics.push(diagnostic);
        }

        // Vérification en-tête constitutionnel
        const hasConstitutionalHeader = this.checkConstitutionalHeader(text);
        if (!hasConstitutionalHeader) {
            const diagnostic = new vscode.Diagnostic(
                new vscode.Range(0, 0, 0, 0),
                'Fichier manque l\'en-tête constitutionnel AGI',
                vscode.DiagnosticSeverity.Warning
            );
            diagnostic.code = 'AGI-HEADER-001';
            diagnostic.source = 'AGI Constitutional Linter';
            diagnostics.push(diagnostic);
        }

        this.diagnosticCollection.set(document.uri, diagnostics);
    }

    checkConstitutionalHeader(content) {
        const constitutionalMarkers = [
            'Rôle Fondamental',
            'Conforme AGI.md',
            'CHEMIN:',
            'Conformité Architecturale'
        ];
        
        const firstChars = content.substring(0, 500);
        return constitutionalMarkers.some(marker => firstChars.includes(marker));
    }
}

function activate(context) {
    const linter = new AGIConstitutionalLinter();

    // Linter en temps réel
    vscode.workspace.onDidChangeTextDocument(event => {
        linter.lintDocument(event.document);
    });

    vscode.workspace.onDidOpenTextDocument(document => {
        linter.lintDocument(document);
    });

    // Commande d'audit complet
    const auditCommand = vscode.commands.registerCommand('agiLinter.auditProject', () => {
        const terminal = vscode.window.createTerminal('AGI Audit');
        terminal.sendText('python run_agi_audit.py --full --target .');
        terminal.show();
    });

    context.subscriptions.push(linter.diagnosticCollection, auditCommand);
}

function deactivate() {}

module.exports = { activate, deactivate };
