#!/bin/bash
#
# potcar.sh -- assemble a POTCAR from a local PAW pseudopotential repository.
#
# Usage:   bash potcar.sh In As
#          (the order MUST match line 6 of POSCAR)
#
# Edit POTCAR_REPO below to point to your local potpaw_PBE folder.
# A typical NERSC layout is /global/common/software/m####/potpaw_PBE.

POTCAR_REPO="<PATH/TO/potpaw_PBE>"

if [ -z "$1" ]; then
    echo "Usage: bash potcar.sh <element1> [element2 ...]" >&2
    exit 1
fi

if [ -f POTCAR ]; then
    mv -f POTCAR POTCAR.old
    echo "Existing POTCAR moved to POTCAR.old"
fi

for element in "$@"; do
    src="$POTCAR_REPO/$element/POTCAR"
    src_z="$POTCAR_REPO/$element/POTCAR.Z"
    src_gz="$POTCAR_REPO/$element/POTCAR.gz"

    if [ -f "$src" ]; then
        cat "$src" >> POTCAR
    elif [ -f "$src_z" ]; then
        zcat "$src_z" >> POTCAR
    elif [ -f "$src_gz" ]; then
        gunzip -c "$src_gz" >> POTCAR
    else
        echo "Warning: no POTCAR for element '$element' under $POTCAR_REPO -- skipped." >&2
    fi
done

echo "Wrote POTCAR for: $*"
grep 'TITEL' POTCAR
