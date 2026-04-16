#!/bin/bash
# =============================================================================
# Test script to validate documentation changes in Basic_training/docs
# Run: bash test_docs.sh
# =============================================================================

DOCS_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0
WARN=0

pass() { echo "  [PASS] $1"; ((PASS++)); }
fail() { echo "  [FAIL] $1"; ((FAIL++)); }
warn() { echo "  [WARN] $1"; ((WARN++)); }

echo "============================================="
echo "  Documentation Validation Tests"
echo "============================================="
echo ""

# ----- 1. Fix: scp -rf → scp -r (no -f flag) -----
echo "--- 1. scp flag fix (linux_basic) ---"
FILE="$DOCS_DIR/HPC Onboard/linux_basic/index.md"
if grep -q 'scp -rf' "$FILE"; then
    fail "Still contains invalid 'scp -rf' (should be 'scp -r')"
else
    pass "'scp -rf' removed — only 'scp -r' present"
fi

# ----- 2. Fix: "ternimal" → "terminal" -----
echo "--- 2. Typo fix: ternimal (linux_basic) ---"
if grep -qi 'ternimal' "$FILE"; then
    fail "Typo 'ternimal' still present"
else
    pass "Typo 'ternimal' fixed to 'terminal'"
fi

# ----- 3. Fix: sudo apt note for HPC -----
echo "--- 3. sudo apt HPC note (linux_basic) ---"
if grep -q 'do not have.*sudo' "$FILE" || grep -q 'not.*have.*sudo' "$FILE"; then
    pass "Note about sudo not being available on HPC is present"
else
    fail "Missing note about sudo not being available on HPC clusters"
fi

# ----- 4. Fix: conda activate in batch scripts needs init -----
echo "--- 4. conda init in batch scripts (linux_basic) ---"
if grep -q 'conda shell.bash hook' "$FILE"; then
    pass "conda initialization added in linux_basic batch script example"
else
    fail "Missing 'eval \"\$(conda shell.bash hook)\"' in linux_basic"
fi

echo "--- 4b. conda init in batch scripts (slurm_basic) ---"
FILE2="$DOCS_DIR/HPC Onboard/slurm_basic/index.md"
if grep -q 'conda shell.bash hook' "$FILE2"; then
    pass "conda initialization added in slurm_basic batch script example"
else
    fail "Missing 'eval \"\$(conda shell.bash hook)\"' in slurm_basic"
fi

# ----- 5. Fix: srun -n explanation -----
echo "--- 5. srun -n clarification (slurm_basic) ---"
if grep -q 'MPI tasks' "$FILE2"; then
    pass "srun -n explained as MPI tasks"
else
    fail "Missing MPI tasks explanation for srun -n"
fi

# ----- 6. Fix: Trace code fence mismatch -----
echo "--- 6. Code fence fix (Trace) ---"
FILE3="$DOCS_DIR/HPC Onboard/Trace/index.md"
# Count lines with exactly 4 backticks (not 3)
FOUR_TICKS=$(grep -c '````' "$FILE3" 2>/dev/null | head -1 || echo 0)
if [ "${FOUR_TICKS:-0}" -eq 0 ]; then
    pass "No mismatched 4-backtick code fences in Trace"
else
    fail "Found $FOUR_TICKS lines with 4-backtick fences in Trace"
fi

# ----- 7. Fix: Chrome extension URL removed -----
echo "--- 7. Chrome extension URL fix (Tutorial_1) ---"
FILE4="$DOCS_DIR/Tutorials/Tutorial_1/index.md"
if grep -q 'chrome-extension://' "$FILE4"; then
    fail "Chrome extension URL still present in Tutorial_1"
else
    pass "Chrome extension URL removed"
fi
# Check the correct URL is there
if grep -q 'https://fhi-aims.org/uploads/documents/FHI-aims' "$FILE4"; then
    pass "Direct FHI-aims manual URL present"
else
    fail "FHI-aims manual URL missing"
fi

# ----- 8. Fix: "successdully" → "successfully" -----
echo "--- 8. Typo fix: successdully (Tutorial_1) ---"
if grep -qi 'successdully' "$FILE4"; then
    fail "Typo 'successdully' still present"
else
    pass "Typo fixed to 'successfully'"
fi

# ----- 9. Fix: Vertical/Adiabatic IP/EA definitions -----
echo "--- 9. Vertical/Adiabatic definition fix (Tutorial_1) ---"
if grep -q 'excited state.*ground state.*geometry.*held constant' "$FILE4"; then
    fail "Old incorrect 'excited state' definition still present"
else
    pass "Old 'excited state' wording removed"
fi
if grep -q 'neutral ground-state geometry' "$FILE4"; then
    pass "Correct 'neutral ground-state geometry' definition present"
else
    fail "Missing correct vertical IP/EA definition"
fi
if grep -q 'ionized species.*relaxed' "$FILE4"; then
    pass "Correct adiabatic definition (ionized species relaxed) present"
else
    fail "Missing correct adiabatic IP/EA definition"
fi

# ----- 10. Fix: KJ/mol → kJ/mol and "timing" → "multiplying by" -----
echo "--- 10. Unit and wording fix (Tutorial_1) ---"
if grep -q 'KJ/mol' "$FILE4"; then
    fail "'KJ/mol' still present (should be 'kJ/mol')"
else
    pass "'kJ/mol' used correctly (lowercase k)"
fi
if grep -q 'by timing the' "$FILE4"; then
    fail "'timing' still present (should be 'multiplying by')"
else
    pass "'multiplying by' used correctly"
fi

# ----- 11. Fix: BFGS ≠ TRM (Tutorial_2) -----
echo "--- 11. BFGS/TRM fix (Tutorial_2) ---"
FILE5="$DOCS_DIR/Tutorials/Tutorial_2/index.md"
if grep -q 'same as trm' "$FILE5"; then
    fail "'same as trm' still present — BFGS and TRM are different algorithms"
else
    pass "BFGS and TRM correctly described as different algorithms"
fi

# ----- 12. Fix: HSE06 unit clarification -----
echo "--- 12. HSE06 unit clarification (Tutorial_2) ---"
if grep -q 'hse_unit bohr.*required' "$FILE5" || grep -q 'bohr.*required' "$FILE5"; then
    pass "HSE06 hse_unit bohr requirement noted"
else
    fail "Missing clarification that hse_unit bohr is required with 0.11"
fi

# ----- 13. Fix: use_dipole_correction .true. kept -----
echo "--- 13. use_dipole_correction .true. preserved (Tutorial_3) ---"
FILE6="$DOCS_DIR/Tutorials/Tutorial_3/index.md"
if grep -q 'use_dipole_correction.*\.true\.' "$FILE6"; then
    pass "use_dipole_correction .true. preserved (user confirmed it works)"
else
    fail "use_dipole_correction .true. was removed but user said it works"
fi

# ----- 14. Fix: compensate_multipole_errors .true. kept -----
echo "--- 14. compensate_multipole_errors .true. preserved (Tutorial_3) ---"
if grep -q 'compensate_multipole_errors.*\.true\.' "$FILE6"; then
    pass "compensate_multipole_errors .true. preserved (user confirmed it works)"
else
    fail "compensate_multipole_errors .true. was removed but user said it works"
fi

# ----- 15. Fix: graphene lattice vector precision -----
echo "--- 15. Graphene lattice vector precision (Tutorial_3) ---"
if grep -q '2\.13000000' "$FILE6"; then
    fail "Imprecise lattice vector 2.13000000 still present (should be 2.13042)"
else
    pass "Lattice vector truncation fixed"
fi
if grep -q '2\.13042' "$FILE6"; then
    pass "Precise lattice vector 2.13042 present"
else
    fail "Missing corrected lattice vector value 2.13042"
fi

# ----- 16. Addition: occupation smearing for metals -----
echo "--- 16. Occupation smearing addition (Tutorial_2) ---"
if grep -q 'occupation_type.*gaussian' "$FILE5"; then
    pass "Occupation smearing guidance added for metals"
else
    fail "Missing occupation smearing guidance for Fe k-convergence"
fi
if grep -q '0\.1' "$FILE5" && grep -q 'occupation_type' "$FILE5"; then
    pass "Default broadening width 0.1 eV documented"
else
    warn "Check broadening width value"
fi

# ----- 17. Addition: band gap extraction -----
echo "--- 17. Band gap extraction section (Tutorial_2) ---"
if grep -q 'How to extract the band gap' "$FILE5"; then
    pass "Band gap extraction section added"
else
    fail "Missing band gap extraction section"
fi
if grep -q 'Direct.*gap.*Indirect.*gap\|Direct vs.*indirect' "$FILE5"; then
    pass "Direct vs indirect gap explained"
else
    fail "Missing direct vs indirect gap explanation"
fi
if grep -q 'ESTIMATED overall HOMO-LUMO gap' "$FILE5"; then
    pass "grep command for HOMO-LUMO gap from aims.out documented (correct format)"
else
    fail "Missing or incorrect aims.out grep command for band gap"
fi
if grep -q 'HOMO.*is the VBM\|HOMO.*VBM\|for a crystal.*HOMO.*VBM' "$FILE5"; then
    pass "HOMO-LUMO vs VBM-CBM terminology clarified for periodic systems"
else
    fail "Missing clarification that HOMO=VBM and LUMO=CBM in periodic systems"
fi
if grep -q 'VBM.*CBM\|valence band maximum.*conduction band minimum' "$FILE5"; then
    pass "VBM/CBM terminology defined"
else
    fail "Missing VBM/CBM definitions"
fi

# ----- 18. Addition: relax_unit_cell explanation -----
echo "--- 18. relax_unit_cell explanation (Tutorial_2) ---"
if grep -q 'fixed_angles.*lengths.*angles\|optimizes lattice vector lengths' "$FILE5"; then
    pass "fixed_angles vs full relax_unit_cell explained"
else
    fail "Missing relax_unit_cell fixed_angles vs full explanation"
fi

# ----- 19. Addition: dipole correction explanation -----
echo "--- 19. Dipole correction explanation (Tutorial_3) ---"
if grep -q 'artificial electric field\|periodic boundary.*vacuum' "$FILE6"; then
    pass "Dipole correction purpose explained"
else
    fail "Missing explanation of why dipole correction is needed for 2D"
fi

# ----- 20. Cross-file: no broken image references -----
echo "--- 20. Image references ---"
ALL_OK=true
for md_file in "$DOCS_DIR"/Tutorials/Tutorial_*/index.md; do
    # Extract image src paths
    grep -oP 'src="([^"]+)"' "$md_file" | sed 's/src="//;s/"//' | while read -r img_path; do
        md_dir="$(dirname "$md_file")"
        full_path="$md_dir/$img_path"
        if [ ! -f "$full_path" ]; then
            fail "Broken image: $img_path in $(basename "$(dirname "$md_file")")/index.md"
            ALL_OK=false
        fi
    done
done
if $ALL_OK; then
    pass "All image references resolve to existing files"
fi

# ----- 21. Markdown: code blocks are balanced -----
echo "--- 21. Code block balance ---"
for md_file in "$DOCS_DIR"/Tutorials/Tutorial_*/index.md "$DOCS_DIR"/HPC\ Onboard/*/index.md; do
    name="$(basename "$(dirname "$md_file")")"
    FENCES=$(grep -c '```' "$md_file" 2>/dev/null || echo 0)
    if [ $((FENCES % 2)) -ne 0 ]; then
        fail "Unbalanced code fences ($FENCES) in $name/index.md"
    else
        pass "Code fences balanced ($FENCES) in $name/index.md"
    fi
done

# =============================================
echo ""
echo "============================================="
echo "  Results: $PASS passed, $FAIL failed, $WARN warnings"
echo "============================================="

if [ "$FAIL" -gt 0 ]; then
    exit 1
else
    echo "  All tests passed!"
    exit 0
fi
