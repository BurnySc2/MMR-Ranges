import React, { Component } from "react"
import data_header from "../data/data_header.json"

interface Props {}
interface State {}

export default class Header extends Component<Props, State> {
    state = {}

    render() {
        let header_class = "text-center flex flex-col items-center"
        let title_class = "hover:bg-gray-400 text-4xl"
        let header_row_class = "border-t border-b"

        let table_class = "table-fixed"
        let row_items = "px-4 py-2"
        let row_first_item = "bg-gray-700 hover:bg-gray-800 text-white"
        let row_second_item = "bg-gray-100 hover:bg-gray-400"

        return (
            <div className={header_class}>
                <div className={title_class}>{`MMR Ranges - Last update: ${data_header.time}`}</div>
                <table className={table_class}>
                    <tr className={header_row_class}>
                        <td className={`${row_items} ${row_first_item}`}>Season number</td>
                        <td className={`${row_items} ${row_second_item}`}>{data_header.season}</td>
                    </tr>
                    <tr className={header_row_class}>
                        <td className={`${row_items} ${row_first_item}`}>Season start</td>
                        <td className={`${row_items} ${row_second_item}`}>
                            {data_header.season_start}
                        </td>
                    </tr>
                    <tr className={header_row_class}>
                        <td className={`${row_items} ${row_first_item}`}>Season end</td>
                        <td className={`${row_items} ${row_second_item}`}>
                            {data_header.season_end}
                        </td>
                    </tr>
                </table>
            </div>
        )
    }
}
