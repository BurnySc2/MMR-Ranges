import React from "react"

export default function Footer(props: any) {
    return (
        <div className={"flex justify-center"}>
            <a
                className="hover:bg-blue-600 bg-blue-200 font-semibold mx-1 py-2 px-4 rounded select-none h-10"
                href="https://github.com/BurnySc2/MMR-Ranges"
                target="_blank"
                rel="noopener noreferrer"
            >
                Source code
            </a>
        </div>
    )
}
