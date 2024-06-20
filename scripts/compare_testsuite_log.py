#!/usr/bin/env python3
from pathlib import Path
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from collections import Counter


@dataclass
class LibName:
    """Named Tuple for arch abi model"""

    arch: str
    abi: str
    model: str
    multilib: bool
    other_args: str

    def __init__(self, arch: str, abi: str, model: str, multilib: bool, other_args: str):
        self.arch = arch.strip().lower()
        self.abi = abi.strip().lower()
        self.model = model.strip().lower()
        self.multilib = multilib
        self.other_args = other_args.strip()

    def __str__(self):
        return " ".join((self.arch, self.abi, self.model)) + (" multilib" if self.multilib else "") + f" {self.other_args}"

    def __hash__(self):
        return hash((self.arch, self.abi, self.model, self.multilib, self.other_args))


@dataclass
class Description:
    """Named Tuple for tool arch abi model"""

    tool: str
    libname: LibName

    def __hash__(self):
        return hash((self.tool, self.libname))


@dataclass
class GlibcFailure:
    """Failure class to group lib's tool failures"""

    glibc_failure_count: Tuple[str, str] = ("0", "0")

    glibc: Dict[str, List[str]] = field(default_factory=dict)

    def __str__(self):
        result = ""
        if len(self.glibc) > 0:
            result += "### glibc failures\n"
            for _, case in self.glibc.items():
                result += "\n".join(case)
        return result

    def count_failures(
        self, unique_failure_dict: Dict[str, List[str]]
    ) -> Tuple[str, str]:
        """parse (total failures count, unique failures count)"""
        unique_count = len(unique_failure_dict)
        total_count = 0
        for unique_failures in unique_failure_dict:
            total_count += len(unique_failure_dict[unique_failures])
        return (str(total_count), str(unique_count))

    def __setitem__(self, key: str, value: Dict[str, List[str]]):
        if key == "glibc":
            self.glibc = value
            self.glibc_failure_count = self.count_failures(value)


    def __getitem__(self, key: str):
        if key == "glibc":
            return self.glibc
        elif key == "glibc_failure_count":
            return self.glibc_failure_count

@dataclass
class ClassifedGlibcFailures:
    """Failures class to distinguish the failure types"""

    resolved: Dict[LibName, GlibcFailure] = field(default_factory=dict)
    unresolved: Dict[LibName, GlibcFailure] = field(default_factory=dict)
    new: Dict[LibName, GlibcFailure] = field(default_factory=dict)

    def failure_dict_to_string(
        self, failure_dict: Dict[LibName, GlibcFailure], failure_name: str
    ):
        result = f"# {failure_name}\n"
        for libname, glibcfailure in failure_dict.items():
            result += f"## {libname}\n"
            result += str(glibcfailure)
        return result

    def __str__(self):
        result = self.failure_dict_to_string(self.resolved, "Resolved Failures")
        result += self.failure_dict_to_string(self.unresolved, "Unresolved Failures")
        result += self.failure_dict_to_string(self.new, "New Failures")
        return result


def parse_arguments():
    parser = argparse.ArgumentParser(description="Testsuite Compare Options")
    parser.add_argument(
        "-plog",
        "--previous-log",
        metavar="<filename>",
        required=True,
        type=str,
        help="Path to the previous testsuite result log",
    )
    parser.add_argument(
        "-phash",
        "--previous-hash",
        metavar="<string>",
        required=True,
        type=str,
        help="Commit hash of the previous Glibc testsuite log",
    )

    parser.add_argument(
        "-clog",
        "--current-log",
        metavar="<filename>",
        required=True,
        type=str,
        help="Path to the current testsuite result log",
    )

    parser.add_argument(
        "-chash",
        "--current-hash",
        metavar="<string>",
        required=True,
        type=str,
        help="Commit hash of the current Glibc testsuite log",
    )

    parser.add_argument(
        "-o",
        "--output-markdown",
        default="./testsuite.md",
        metavar="<filename>",
        type=str,
        help="Path to the current testsuite result log",
    )

    parser.add_argument(
        '-ccommitted',
        '--current-hash-committed',
        help="The current hash is an existing Glibc hash",
        action='store_true'
    )

    return parser.parse_args()


def is_description(line: str) -> bool:
    """checks if the line is a tool description"""
    if line.startswith("\t\t==="):
        return True
    return False


def parse_description(line: str, multilib: bool) -> Description:
    """returns 'tool arch abi model'"""
    descriptions = line.split(" ")
    tool = descriptions[1][:-1]
    arch = descriptions[5]
    abi = descriptions[6]
    model = descriptions[7]
    other_args = " ".join(descriptions[8:-1])
    description = Description(tool, LibName(arch, abi, model, multilib, other_args))
    return description


def parse_failure_name(failure_line: str) -> str:
    failure_components = failure_line.split(" ")
    if len(failure_components) < 2:
        raise ValueError(f"Invalid Failure Log: {failure_line}")
    return failure_components[1]


def parse_testsuite_failures(log_path: str) -> Dict[Description, List[str]]:
    """
    parse testsuite failures from the log in the path
    """
    if not Path(log_path).exists():
        raise ValueError(f"Invalid Path: {log_path}")
    failures: Dict[Description, List[str]] = {}
    with open(log_path, "r") as file:
        description = None
        for line in file:
            if line == "\n":
                break
            if is_description(line):
                description = parse_description(line, "non-multilib" not in log_path)
                failures[description] = []
                continue
            failures[description].append(line)
    return failures


def classify_by_unique_failure(failure_set: List[str]):
    failure_dictionary: Dict[str, List[str]] = {}
    for failure in failure_set:
        failure_name = parse_failure_name(failure)
        if failure_name not in failure_dictionary:
            failure_dictionary[failure_name] = []
        failure_dictionary[failure_name].append(failure)
    return failure_dictionary

def list_difference(a: List[str], b: List[str]):
    count = Counter(a)
    count.subtract(b)
    diff = []
    for x in a:
        if count[x] > 0:
            count[x] -= 1
            diff.append(x)

    return diff

def list_intersect(a: List[str], b: List[str]):
    return list((Counter(a) & Counter(b)).elements())

def compare_testsuite_log(previous_log_path: str, current_log_path: str):
    """
    returns (resolved_failures, unresolved_failures, new_failures)
    failures: Dict[tool combination label : Dict[unique testsuite name: Set[testsuite failure log]]]
    tool combination: 'tool arch abi model'
    """
    previous_failures = parse_testsuite_failures(previous_log_path)
    current_failures = parse_testsuite_failures(current_log_path)

    previous_failures_descriptions = set(previous_failures.keys())
    current_failures_descriptions = set(current_failures.keys())
    resolved_descriptions = (
        previous_failures_descriptions - current_failures_descriptions
    )
    unresolved_descriptions = (
        previous_failures_descriptions & current_failures_descriptions
    )
    new_descriptions = current_failures_descriptions - previous_failures_descriptions

    classified_glibc_failures = ClassifedGlibcFailures()
    for description in resolved_descriptions:
        classified_dict = classify_by_unique_failure(previous_failures[description])
        if len(classified_dict):
            classified_glibc_failures.resolved.setdefault(
                description.libname, GlibcFailure()
            )
            classified_glibc_failures.resolved[description.libname][
                description.tool
            ] = classified_dict

    for description in new_descriptions:
        classified_dict = classify_by_unique_failure(current_failures[description])
        if len(classified_dict):
            classified_glibc_failures.new.setdefault(description.libname, GlibcFailure())
            classified_glibc_failures.new[description.libname][
                description.tool
            ] = classified_dict

    for description in unresolved_descriptions:
        resolved_set = list_difference(previous_failures[description], current_failures[description])
        unresolved_set = list_intersect(previous_failures[description], current_failures[description])
        new_set = list_difference(current_failures[description], previous_failures[description])
        classified_dict = classify_by_unique_failure(resolved_set)
        if len(classified_dict):
            classified_glibc_failures.resolved.setdefault(
                description.libname, GlibcFailure()
            )
            classified_glibc_failures.resolved[description.libname][
                description.tool
            ] = classified_dict

        classified_dict = classify_by_unique_failure(unresolved_set)
        if len(classified_dict):
            classified_glibc_failures.unresolved.setdefault(
                description.libname, GlibcFailure()
            )
            classified_glibc_failures.unresolved[description.libname][
                description.tool
            ] = classified_dict

        classified_dict = classify_by_unique_failure(new_set)
        if len(classified_dict):
            classified_glibc_failures.new.setdefault(description.libname, GlibcFailure())
            classified_glibc_failures.new[description.libname][
                description.tool
            ] = classified_dict

    return classified_glibc_failures


def glibcfailure_to_summary(failure: Dict[LibName, GlibcFailure], failure_name: str, previous_hash: str, current_hash: str, current_hash_committed: bool):
    tool = "glibc"
    result = f"|{failure_name}|{tool}|Previous Hash|\n"
    result +="|---|---|---|\n"
    for libname, glibcfailure in failure.items():
        result += f"|{libname}|"
        tool_failure_key = f"{tool}_failure_count"
        # convert tuple of counts to string
        result += f"{'/'.join(glibcfailure[tool_failure_key])}|"

        if current_hash_committed:
            result += f"[{previous_hash}](https://github.com/bminor/glibc/compare/{previous_hash}...{current_hash})|\n"
        else:
           result += f"https://github.com/bminor/glibc/commit/{previous_hash}|\n"
    result += "\n"
    return result


def failures_to_summary(failures: ClassifedGlibcFailures, previous_hash: str, current_hash: str, current_hash_committed: bool):
    result = "# Summary\n"
    result += glibcfailure_to_summary(failures.resolved, "Resolved Failures", previous_hash, current_hash, current_hash_committed)
    result += glibcfailure_to_summary(failures.unresolved, "Unresolved Failures", previous_hash, current_hash, current_hash_committed)
    result += glibcfailure_to_summary(failures.new, "New Failures", previous_hash, current_hash, current_hash_committed)
    result += "\n"
    return result


def failures_to_markdown(
    failures: ClassifedGlibcFailures, previous_hash: str, current_hash: str, current_hash_committed: bool
) -> str:
    result = f"""---
title: {previous_hash}->{current_hash}
labels: bug
---\n"""
    result += failures_to_summary(failures, previous_hash, current_hash, current_hash_committed)
    result += str(failures)
    return result


def is_result_valid(log_path: str):
    if not Path(log_path).exists():
        raise ValueError(f"Invalid Path: {log_path}")
    with open(log_path, "r") as file:
        summary_flag = False
        while True:
            line = file.readline()
            if not line:
                break
            if line.startswith(
                "               ========= Summary of glibc testsuite ========="
            ):
                summary_flag = True
                break
        if summary_flag == False:
            return False
        # Directly read the case line
        file.readline()
        file.readline()

        line = file.readline()
        # Remove Non-case elements
        splitted = line.split("|")[1]
        case_number = splitted.strip()
        # Test hasn't been executed for the tool
        if case_number == "":
            return False
        return True

def compare_logs(previous_hash: str, previous_log: str, current_hash: str, current_log: str, output_markdown: str, current_hash_committed: bool):
    if not is_result_valid(previous_log):
        raise RuntimeError(f"{previous_log} doesn't include Summary of the testsuite")
    if not is_result_valid(current_log):
        raise RuntimeError(f"{current_log} doesn't include Summary of the testsuite")
    failures = compare_testsuite_log(previous_log, current_log)
    markdown = failures_to_markdown(failures, previous_hash, current_hash, current_hash_committed)
    with open(output_markdown, "w") as markdown_file:
        markdown_file.write(markdown)


def main():
    args = parse_arguments()
    compare_logs(args.previous_hash, args.previous_log, args.current_hash, args.current_log, args.output_markdown, args.current_hash_committed)


if __name__ == "__main__":
    main()