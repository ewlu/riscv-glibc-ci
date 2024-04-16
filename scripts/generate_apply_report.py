import argparse
import re

def parse_arguments():
    parser = argparse.ArgumentParser(description="Apply patch report generator")
    parser.add_argument(
        "-patch",
        "--patch-name",
        required=True,
        metavar="<string>",
        type=str,
        help="Patch name",
    )
    parser.add_argument(
        "-bhash",
        "--base-hash",
        metavar="<string>",
        default="",
        type=str,
        help="Baseline hash",
    )
    parser.add_argument(
        "-bstatus",
        "--base-status",
        required=True,
        metavar="<string>",
        type=str,
        help="Baseline status",
    )
    parser.add_argument(
        "-o",
        "--output-markdown",
        default="./issue.md",
        metavar="<filename>",
        type=str,
        help="Output file name",
    )
    return parser.parse_args()

def build_status(bhash:str, bstatus: str):
    result = "## Apply Status\n"
    result += "|Target|Status|\n"
    result += "|---|---|\n"
    result += f"|Baseline hash: https://github.com/bminor/glibc/commit/{bhash}|{bstatus}|\n"
    return result

def generate_report(patch_name: str, bhash: str, bstatus: str):
    result = ""
    if bstatus != "pending":
        bstatus = "Applied" if bstatus == "true" else "Failed"
    result += build_status(bhash, bstatus)
    result += "\n"
    if bstatus == "pending":
        return result
    elif bstatus == "Failed":
        result += "## Command\n"
        result += "```\n"
        result += "> git am ../patches/*.patch --whitespace=fix -q --3way --empty=drop\n"
        result += "```\n"
        result += "## Output\n"
        result += "```\n"
        with open("hash_output/apply.log", "r") as f:
            result += f.read()
        result += "```"
#     elif bstatus == "Failed" and tstatus == "Applied":
#         result += "## Notes\n"
#         result += f"""Failed to apply to the [post-commit baseline](https://github.com/patrick-rivos/gcc-postcommit-ci/issues?q=is%3Aissue+{bhash}). This can happen
# if your commit requires a recently-commited patch in order to apply.
# The pre-commit CI will only perform a build since it doesn't know what
# dejagnu testsuite failures are expected on the tip-of-tree.
#
# If you would like us to re-run this patch once the [baseline](https://github.com/patrick-rivos/gcc-postcommit-ci/issues?q=is%3Aissue) reaches a
# different hash, please email us at patchworks-ci@rivosinc.com with a link
# to your patch.
# """
#     elif bstatus == "Applied" and tstatus == "Failed":
#         result += "## Notes\n"
#         result += """Failed to apply to tip-of-tree. The patch will still
# be tested against the baseline hash. A rebase may be necessary
# before merging.
# """
    else:
        result += "## Notes\n"
        result += "Patch applied successfully"

    result += "\n"

    return result

def main():
    args = parse_arguments()
    issue = generate_report(args.patch_name, args.base_hash, args.base_status)
    with open(args.output_markdown, "w") as f:
        f.write(issue)

if __name__ == "__main__":
    main()