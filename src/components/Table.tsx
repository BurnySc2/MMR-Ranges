import React, { Component } from "react"

interface Props {
    // Each row has 4 entries: Description (GrandMaster), then entry for US, EU and KR server
    data: Array<string[]>
    enabled: boolean
}
interface State {}

export default class Table extends Component<Props, State> {
    state = {}

    render() {
        if (!this.props.enabled) {
            return <div></div>
        }
        // console.log(this.props.data)
        let content_class = "flex flex-col items-center"
        let table_class = "table-fixed"
        let table_row_class = "hover:bg-gray-400"
        let table_header_class = "p-4"
        let table_cell_class = "px-4 py-2 text-center font-semibold border-t-2"

        let table = this.props.data.map((row_data: string[], index: number) => {
            // console.log(index)
            // console.log(row_data)
            let row = row_data.map((entry: string, index2: number) => {
                // console.log(index2)
                // console.log(entry)

                if (index === 0) {
                    return <th className={table_header_class}>{entry}</th>
                } else {
                    return <td className={table_cell_class}>{entry}</td>
                }
            })
            return <tr className={table_row_class}>{row}</tr>
        })

        let table_full = <table className={table_class}>{table}</table>

        return <div className={content_class}>{table_full}</div>
    }
}
