#!/bin/bash
# =============================================================================
# Integration test: Run FHI-aims calculations to validate tutorial instructions
#
# Tests:
#   1. Si band gap: verify 'ESTIMATED overall HOMO-LUMO gap' appears in aims.out
#      and reports an indirect gap consistent with known Si LDA gap (~0.5 eV)
#   2. Fe k-conv (no smearing): run Fe BCC metal to show baseline behavior
#   3. Fe k-conv (with smearing): run same with occupation_type gaussian 0.1
#      to confirm the keyword is accepted and calculation converges
#
# Usage:
#   bash run_tests.sh          # submit all jobs
#   bash run_tests.sh --check  # check results after jobs finish
# =============================================================================

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---- SUBMIT MODE ----
if [ "$1" != "--check" ]; then
    echo "============================================="
    echo "  Submitting FHI-aims test jobs"
    echo "============================================="

    for test_case in si_bandgap fe_kconv_no_smear fe_kconv_smear; do
        echo ""
        echo "--- Submitting: $test_case ---"
        cd "$TEST_DIR/$test_case"
        # Verify input files
        if [ ! -f geometry.in ] || [ ! -f control.in ] || [ ! -f submit.sh ]; then
            echo "[ERROR] Missing input files in $test_case"
            continue
        fi
        echo "  geometry.in: $(grep -c 'atom' geometry.in) atom(s)"
        echo "  control.in:  xc=$(grep '^xc' control.in | awk '{print $2}')"
        echo "  k_grid:      $(grep '^k_grid' control.in | awk '{print $2,$3,$4}')"
        if grep -q 'occupation_type' control.in; then
            echo "  smearing:    $(grep 'occupation_type' control.in)"
        fi

        JOB_ID=$(sbatch submit.sh 2>&1)
        echo "  $JOB_ID"
    done

    echo ""
    echo "============================================="
    echo "  Jobs submitted. Monitor with: squeue -u \$USER"
    echo "  After completion, run: bash run_tests.sh --check"
    echo "============================================="
    exit 0
fi

# ---- CHECK MODE ----
echo "============================================="
echo "  Checking FHI-aims test results"
echo "============================================="

PASS=0
FAIL=0

pass() { echo "  [PASS] $1"; ((PASS++)); }
fail() { echo "  [FAIL] $1"; ((FAIL++)); }

# ---------- TEST 1: Si band gap ----------
echo ""
echo "--- Test 1: Si band gap calculation ---"
SI_OUT="$TEST_DIR/si_bandgap/aims.out"

if [ ! -f "$SI_OUT" ]; then
    fail "aims.out not found — job may not have finished"
else
    # Check job completed successfully
    if grep -q 'Have a nice day.' "$SI_OUT"; then
        pass "Si calculation completed successfully"
    else
        fail "Si calculation did not finish (no 'Have a nice day.')"
    fi

    # Check ESTIMATED overall HOMO-LUMO gap exists
    GAP_LINE=$(grep 'ESTIMATED overall HOMO-LUMO gap' "$SI_OUT" | tail -1)
    if [ -n "$GAP_LINE" ]; then
        pass "Found: $GAP_LINE"

        # Extract gap value
        GAP_VAL=$(echo "$GAP_LINE" | grep -oP '[\d.]+(?= eV)')
        if [ -n "$GAP_VAL" ]; then
            # Si LDA gap should be ~0.4-0.7 eV (LDA underestimates; expt ~1.17 eV)
            IN_RANGE=$(echo "$GAP_VAL > 0.2 && $GAP_VAL < 1.5" | bc -l 2>/dev/null)
            if [ "$IN_RANGE" = "1" ]; then
                pass "Band gap $GAP_VAL eV is in expected LDA range (0.2-1.5 eV)"
            else
                fail "Band gap $GAP_VAL eV outside expected range"
            fi
        fi
    else
        fail "'ESTIMATED overall HOMO-LUMO gap' NOT found in aims.out"
    fi

    # Check direct/indirect gap info
    if grep -q 'indirect band gap' "$SI_OUT"; then
        pass "Si correctly identified as indirect band gap"
    elif grep -q 'direct band gap' "$SI_OUT"; then
        fail "Si incorrectly identified as direct gap (should be indirect)"
    else
        fail "No direct/indirect gap info found in aims.out"
    fi

    # Check smallest direct gap is reported
    DIRECT_LINE=$(grep 'Smallest direct gap' "$SI_OUT" | tail -1)
    if [ -n "$DIRECT_LINE" ]; then
        pass "Direct gap also reported: $DIRECT_LINE"
    else
        fail "'Smallest direct gap' not found"
    fi

    # Check band structure files were generated
    BAND_FILES=$(ls "$TEST_DIR/si_bandgap"/band100*.out 2>/dev/null | wc -l)
    if [ "$BAND_FILES" -gt 0 ]; then
        pass "Band structure files generated ($BAND_FILES files)"
    else
        fail "No band structure output files (band100*.out) found"
    fi
fi

# ---------- TEST 2: Fe without smearing ----------
echo ""
echo "--- Test 2: Fe BCC without smearing ---"
FE_NO="$TEST_DIR/fe_kconv_no_smear/aims.out"

if [ ! -f "$FE_NO" ]; then
    fail "aims.out not found — job may not have finished"
else
    if grep -q 'Have a nice day.' "$FE_NO"; then
        pass "Fe (no smearing) completed"
    else
        # Metals without smearing may still converge but can be problematic
        if grep -q 'Self-consistency cycle converged' "$FE_NO"; then
            pass "Fe (no smearing) SCF converged"
        else
            fail "Fe (no smearing) did not converge"
        fi
    fi

    # Check total energy
    FE_NO_E=$(grep '| Total energy' "$FE_NO" | tail -1)
    if [ -n "$FE_NO_E" ]; then
        pass "Energy obtained: $FE_NO_E"
    else
        fail "No total energy found"
    fi

    # For a metal: should NOT have a gap, or gap should be ~0
    if grep -q 'ESTIMATED overall HOMO-LUMO gap' "$FE_NO"; then
        FE_GAP=$(grep 'ESTIMATED overall HOMO-LUMO gap' "$FE_NO" | tail -1 | grep -oP '[\d.]+(?= eV)')
        echo "  [INFO] Fe HOMO-LUMO gap (no smearing): $FE_GAP eV"
    else
        echo "  [INFO] No HOMO-LUMO gap reported (expected for metal)"
    fi
fi

# ---------- TEST 3: Fe with smearing ----------
echo ""
echo "--- Test 3: Fe BCC with occupation_type gaussian 0.1 ---"
FE_SM="$TEST_DIR/fe_kconv_smear/aims.out"

if [ ! -f "$FE_SM" ]; then
    fail "aims.out not found — job may not have finished"
else
    if grep -q 'Have a nice day.' "$FE_SM"; then
        pass "Fe (gaussian 0.1) completed successfully"
    else
        if grep -q 'Self-consistency cycle converged' "$FE_SM"; then
            pass "Fe (gaussian 0.1) SCF converged"
        else
            fail "Fe (gaussian 0.1) did not converge"
        fi
    fi

    # Verify smearing was actually used
    if grep -q 'occupation_type' "$FE_SM" || grep -q 'Gaussian broadening' "$FE_SM" || grep -q 'gaussian' "$FE_SM"; then
        pass "Gaussian smearing acknowledged in output"
    else
        echo "  [WARN] Could not confirm smearing in output (check manually)"
    fi

    # Check total energy
    FE_SM_E=$(grep '| Total energy' "$FE_SM" | tail -1)
    if [ -n "$FE_SM_E" ]; then
        pass "Energy obtained: $FE_SM_E"
    else
        fail "No total energy found"
    fi

    # Count SCF iterations — smearing should help convergence
    SCF_ITERS=$(grep -c 'Begin self-consistency iteration' "$FE_SM" 2>/dev/null)
    echo "  [INFO] SCF iterations (with smearing): $SCF_ITERS"
fi

# ---------- SUMMARY ----------
echo ""
echo "============================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "============================================="
[ "$FAIL" -eq 0 ] && echo "  All tests passed!" || exit 1
